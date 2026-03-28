"""
lua_mob_loader.py
-----------------
Scans every scripts/zones/<zone>/mobs/*.lua file and converts each one into
a Python creature template dict that the existing CreatureManager / Creature
system already understands.

No changes needed to any other file for new zones — just drop a .lua file in
the right mobs/ folder and it's automatically live on next server start.

Lua mob file keys consumed:
    Creature.id              -> template "creature_id" (internal, not template_id)
    Creature.name            -> "name"
    Creature.level           -> "level"
    Creature.family          -> "family"
    Creature.classification  -> "classification"  (living/corporeal_undead/non_corporeal_undead)
    Creature.body_type       -> "body_type"
    Creature.hp_base         -> "hp"
    Creature.hp_variance     -> "hp_variance"
    Creature.ds_melee        -> "ds_melee"
    Creature.ds_bolt         -> "ds_bolt"
    Creature.td_spiritual    -> "td"
    Creature.udf             -> "udf"
    Creature.armor_asg       -> "armor_asg"
    Creature.armor_natural   -> "armor_natural"
    Creature.loot_coins      -> treasure["coins"]
    Creature.loot_gems       -> treasure["gems"]
    Creature.loot_magic      -> treasure["magic"]
    Creature.loot_boxes      -> treasure["boxes"]
    Creature.skin            -> "skin"
    Creature.decay_seconds   -> "decay_seconds"
    Creature.crumbles        -> "crumbles"
    Creature.decay_message   -> "decay_message"
    Creature.spawn_rooms     -> "spawn_rooms"  (list block)
    Creature.roam_rooms      -> "wander_rooms" (list block)
    Creature.roam_chance     -> "wander_chance" (converted to 0.0-1.0 float)
    Creature.respawn_seconds -> "respawn_time"
    Creature.max_count       -> "max_count"
    Creature.description     -> "description"

    Creature.attacks block   -> "attacks" list of dicts
    Creature.spells block    -> "spells"  list of dicts (stored separately)
    Creature.abilities block -> "abilities" list of strings
    Creature.immune block    -> "immune"    list of strings
    Creature.resist block    -> "resist"    list of strings
    Creature.special_loot    -> "special_loot" list of strings

Attack verb generation:
    The Lua files store attack type names (e.g. "claw", "broadsword").
    The loader auto-generates verb_first / verb_third strings from those
    so the combat engine gets what it expects without any per-mob manual work.

FIXES (2026-03-22):
    Bug 1 — _parse_attack_block depth logic broke on single-line attack entries.
             { type = "claw", as = 31 } has opens=1 closes=1 so depth stayed 0,
             causing the "if opens and depth > 0" guard to fail and skipping the
             entry entirely. Fixed by evaluating depth BEFORE decrementing closes.

    Bug 2 — Inline empty blocks (Creature.spells = {}) still called the sub-parser
             starting on the NEXT line, causing it to consume the following real
             block (e.g. spawn_rooms). Fixed by checking whether the triggering
             line already contains its own closing brace before dispatching.
"""

import os
import re
import logging

log = logging.getLogger(__name__)

# ── Attack verb templates ─────────────────────────────────────────────────────
# Maps attack type -> (verb_first, verb_third, default_damage_type)
ATTACK_VERBS = {
    "claw":             ("rakes you with its claws",          "rakes {target} with its claws",          "slash"),
    "bite":             ("lunges at you with snapping jaws",  "lunges at {target} with snapping jaws",  "puncture"),
    "sting":            ("stings you with its stinger",       "stings {target} with its stinger",       "puncture"),
    "closed_fist":      ("strikes you with a closed fist",    "strikes {target} with a closed fist",    "crush"),
    "pound":            ("pounds you with massive force",     "pounds {target} with massive force",     "crush"),
    "ensnare":          ("attempts to ensnare you",           "attempts to ensnare {target}",           "crush"),
    "charge":           ("charges at you",                    "charges at {target}",                    "crush"),
    "broadsword":       ("swings a broadsword at you",        "swings a broadsword at {target}",        "slash"),
    "dagger":           ("jabs a dagger at you",              "jabs a dagger at {target}",              "puncture"),
    "scimitar":         ("slashes a scimitar at you",         "slashes a scimitar at {target}",         "slash"),
    "longsword":        ("swings a longsword at you",         "swings a longsword at {target}",         "slash"),
    "two_handed_sword": ("heaves a two-handed sword at you",  "heaves a two-handed sword at {target}",  "slash"),
    "morning_star":     ("swings a morning star at you",      "swings a morning star at {target}",      "crush"),
    "mace":             ("smashes a mace at you",             "smashes a mace at {target}",             "crush"),
    "military_pick":    ("drives a military pick at you",     "drives a military pick at {target}",     "puncture"),
    "pincer":           ("clamps its pincers at you",         "clamps its pincers at {target}",         "crush"),
    "tail_sweep":       ("sweeps its tail at you",            "sweeps its tail at {target}",            "crush"),
    "spear":            ("thrusts a spear at you",            "thrusts a spear at {target}",            "puncture"),
    "handaxe":          ("swings a handaxe at you",           "swings a handaxe at {target}",           "slash"),
    "staff":            ("strikes you with a staff",          "strikes {target} with a staff",          "crush"),
    "gaze":             ("fixes you with a paralyzing gaze",  "fixes {target} with a paralyzing gaze",  "crush"),
    "breath":           ("breathes at you",                   "breathes at {target}",                   "fire"),
    "trample":          ("tramples you underfoot",            "tramples {target} underfoot",            "crush"),
    "rake":             ("rakes you savagely",                "rakes {target} savagely",                "slash"),
    "gore":             ("gores you with its horns",          "gores {target} with its horns",          "puncture"),
    "constrict":        ("constricts you in its coils",       "constricts {target} in its coils",       "crush"),
    "slam":             ("slams into you",                    "slams into {target}",                    "crush"),
    "headbutt":         ("headbutts you",                     "headbutts {target}",                     "crush"),
    "swipe":            ("swipes at you",                     "swipes at {target}",                     "slash"),
    "kick":             ("kicks you",                         "kicks {target}",                         "crush"),
    "stomp":            ("stomps on you",                     "stomps on {target}",                     "crush"),
}

DEFAULT_VERB = ("attacks you", "attacks {target}", "crush")


def _verb_for(attack_type: str, damage_type: str = None):
    """Return (verb_first, verb_third, effective_damage_type) for an attack type."""
    entry = ATTACK_VERBS.get(attack_type.lower(), DEFAULT_VERB)
    effective_dt = damage_type if damage_type else entry[2]
    return entry[0], entry[1], effective_dt


# ── Inline block guard ────────────────────────────────────────────────────────

def _is_inline_block(line: str) -> bool:
    """
    Return True if this line opens AND closes a block on the same line.
    e.g. 'Creature.spells = {}' or 'Creature.resist = { "fire" }'
    This means the sub-parser must NOT be called — there is nothing on
    subsequent lines belonging to this block.
    """
    stripped = line.strip()
    opens  = stripped.count("{")
    closes = stripped.count("}")
    return opens > 0 and opens == closes


# ── Lua list block parser ─────────────────────────────────────────────────────

def _parse_list_block(lines: list, start_idx: int):
    """
    Parse a Lua list block that starts after the opening '{' on the trigger line.
    Returns (list_of_values, next_line_index).
    Values are ints if numeric, strings otherwise (stripped of quotes).

    Handles both one-value-per-line and comma-separated-values-per-line formats:
        6090,              -- one per line
        7163, 7164, 7165,  -- multiple per line (CSV style)
    """
    result = []
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("--"):
            continue
        # Strip inline comments
        if "--" in line:
            line = line[:line.index("--")].strip()
        if not line:
            continue
        # Closing brace with no assignment = end of block
        if "}" in line and "=" not in line:
            break
        # Strip trailing comma from the whole line
        line = line.rstrip(",").strip()
        if not line:
            continue
        # Try single integer first
        try:
            result.append(int(line))
            continue
        except ValueError:
            pass
        # Try comma-separated integers on one line: "7163, 7164, 7165"
        if "," in line:
            parts = [p.strip() for p in line.split(",") if p.strip()]
            try:
                int_parts = [int(p) for p in parts]
                result.extend(int_parts)
                continue
            except ValueError:
                pass
        # Quoted string
        if (line.startswith('"') and line.endswith('"')) or \
           (line.startswith("'") and line.endswith("'")):
            result.append(line[1:-1])
        else:
            result.append(line)
    return result, i


def _parse_attack_block(lines: list, start_idx: int):
    """
    Parse Creature.attacks = { ... } block.

    Handles BOTH single-line and multi-line attack entries:
      Single-line: { type = "claw", as = 31, damage_type = "slash" },
      Multi-line:
        {
            type = "claw",
            as   = 31,
        },

    FIX: depth starts at 1 because the trigger line already consumed the outer
    opening brace ("Creature.attacks = {"). Each inner entry opens at depth>=2
    and closes back to depth==1. The outer block closes when depth hits 0.
    This correctly handles ALL single-line entries without skipping them.
    """
    attacks = []
    i = start_idx
    depth = 1   # already inside the outer block from the trigger line
    current = {}

    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("--"):
            continue

        opens  = line.count("{")
        closes = line.count("}")

        # Apply opens — depth rises when entering an inner entry
        depth += opens

        # Parse key=value pairs when inside an inner entry (depth >= 2)
        if opens and depth >= 2:
            for pair in re.finditer(r'(\w+)\s*=\s*(".*?"|\'.*?\'|\d+)', line):
                k, v = pair.group(1), pair.group(2)
                if v.startswith(("'", '"')):
                    current[k] = v[1:-1]
                else:
                    try:
                        current[k] = int(v)
                    except ValueError:
                        current[k] = v

        # Apply closes
        depth -= closes

        # Closing an inner entry — save whatever we collected
        if closes and current:
            attacks.append(current)
            current = {}

        # depth == 0 means the outer block just closed
        if depth <= 0:
            break

    return attacks, i


def _parse_string_list_block(lines: list, start_idx: int):
    """Parse a { "a", "b", ... } block of strings. Returns (list, next_idx)."""
    result = []
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("--"):
            continue
        if "}" in line and "=" not in line:
            break
        for m in re.finditer(r'"([^"]*)"', line):
            result.append(m.group(1))
    return result, i


def _parse_spells_block(lines: list, start_idx: int):
    """
    Parse Creature.spells = { ... } block.
    Entries may be plain strings OR table dicts:
        { name = "petrifying_gaze", cs = 115, as = 0 },
        "minor_shock",
    Returns (list_of_spell_entries, next_idx). Plain string entries remain
    strings, while table entries are preserved as dicts so runtime AI can use
    the authored spell metadata instead of flattening it away.
    """
    result = []
    i = start_idx
    depth = 1
    current = None

    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("--"):
            continue
        if "--" in line:
            line = line[:line.index("--")].strip()
        if not line:
            continue

        opens = line.count("{")
        closes = line.count("}")

        if depth == 1 and opens == 0:
            for m in re.finditer(r'"([^"]*)"', line):
                val = m.group(1)
                if val:
                    result.append(val)

        if opens > 0 and depth >= 1:
            if depth == 1:
                current = {}
            for pair in re.finditer(r'(\w+)\s*=\s*(".*?"|\'.*?\'|-?\d+(?:\.\d+)?)', line):
                k, v = pair.group(1), pair.group(2)
                if v.startswith(("'", '"')):
                    current[k] = v[1:-1]
                else:
                    try:
                        current[k] = int(v)
                    except ValueError:
                        try:
                            current[k] = float(v)
                        except ValueError:
                            current[k] = v

        depth += opens
        depth -= closes

        if closes and current and depth == 1:
            if current.get("name"):
                result.append(dict(current))
            current = None

        if depth <= 0:
            break

    return result, i


# ── Main file parser ─────────────────────────────────────────────────────────

def parse_mob_lua(filepath: str) -> dict:
    """
    Parse a Creature Lua file and return a Python creature template dict
    ready to be registered in CREATURE_TEMPLATES.
    Returns None if parsing fails.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    except OSError as e:
        log.error("Cannot open mob file %s: %s", filepath, e)
        return None

    lines = [l.rstrip("\r\n") for l in raw_lines]

    scalars      = {}
    attacks_raw  = []
    spells_raw   = []
    abilities    = []
    immune       = []
    resist       = []
    spawn_rooms  = []
    roam_rooms   = []
    special_loot = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1

        if not line or line.startswith("--") or line.startswith("local") \
                or line.startswith("return") or line.startswith("function"):
            continue

        # ── Block dispatchers ──────────────────────────────────────────────
        # IMPORTANT: check for inline blocks first. If the block opens AND
        # closes on the same line (e.g. "Creature.spells = {}"), do NOT call
        # the sub-parser — there is nothing on subsequent lines for it to read,
        # and calling it would silently consume the next real block.

        if "Creature.attacks" in line and "{" in line:
            if _is_inline_block(line):
                attacks_raw = []          # empty inline block
            else:
                attacks_raw, i = _parse_attack_block(lines, i)
            continue

        if "Creature.spells" in line and "{" in line:
            if _is_inline_block(line):
                # Inline spells may still contain names: Creature.spells = { "minor_shock" }
                spells_raw = re.findall(r'"([^"]+)"', line)
            else:
                spells_raw, i = _parse_spells_block(lines, i)
            continue

        if "Creature.abilities" in line and "{" in line:
            if _is_inline_block(line):
                abilities = re.findall(r'"([^"]+)"', line)
            else:
                abilities, i = _parse_string_list_block(lines, i)
            continue

        if "Creature.immune" in line and "{" in line:
            if _is_inline_block(line):
                immune = re.findall(r'"([^"]+)"', line)
            else:
                immune, i = _parse_string_list_block(lines, i)
            continue

        if "Creature.resist" in line and "{" in line:
            if _is_inline_block(line):
                resist = re.findall(r'"([^"]+)"', line)
            else:
                resist, i = _parse_string_list_block(lines, i)
            continue

        if "Creature.spawn_rooms" in line and "{" in line:
            if _is_inline_block(line):
                spawn_rooms = [int(x) for x in re.findall(r'\d+', line)]
            else:
                spawn_rooms, i = _parse_list_block(lines, i)
            continue

        if "Creature.roam_rooms" in line and "{" in line:
            if _is_inline_block(line):
                roam_rooms = [int(x) for x in re.findall(r'\d+', line)]
            else:
                roam_rooms, i = _parse_list_block(lines, i)
            continue

        if "Creature.special_loot" in line and "{" in line:
            if _is_inline_block(line):
                special_loot = re.findall(r'"([^"]+)"', line)
            else:
                special_loot, i = _parse_string_list_block(lines, i)
            continue

        # ── Scalar  Creature.key = value ──────────────────────────────────
        m = re.match(r'^Creature\.(\w+)\s*=\s*(.+)$', line)
        if not m:
            continue
        key = m.group(1)
        val = m.group(2).strip().rstrip(",").strip()

        if "--" in val:
            val = val[:val.index("--")].strip().rstrip(",").strip()

        if val.startswith('"') and val.endswith('"'):
            scalars[key] = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            scalars[key] = val[1:-1]
        elif val.lower() == "true":
            scalars[key] = True
        elif val.lower() == "false":
            scalars[key] = False
        else:
            try:
                scalars[key] = int(val)
            except ValueError:
                try:
                    scalars[key] = float(val)
                except ValueError:
                    scalars[key] = val

    # ── Build template dict ───────────────────────────────────────────────
    name  = scalars.get("name", "")
    level = int(scalars.get("level", 1))

    if not name:
        log.warning("Mob file %s has no name, skipping", filepath)
        return None

    # derive template_id from filename (no extension, lowercase, spaces->_)
    fname = os.path.splitext(os.path.basename(filepath))[0]
    template_id = fname.lower().replace(" ", "_")

    article = "an" if name[0].lower() in "aeiou" else "a"

    # Build attacks list
    built_attacks = []
    for atk in attacks_raw:
        atype = atk.get("type", "claw")
        aas   = int(atk.get("as", level * 5 + 20))
        adt   = atk.get("damage_type", "")
        vf, vt, eff_dt = _verb_for(atype, adt)
        built_attacks.append({
            "name":        atype,
            "as":          aas,
            "damage_type": eff_dt,
            "verb_first":  vf,
            "verb_third":  vt,
            "roundtime":   5,
        })

    if not built_attacks:
        built_attacks = [{
            "name": "attack", "as": level * 5 + 20, "damage_type": "crush",
            "verb_first": "attacks you",
            "verb_third": "attacks {target}",
            "roundtime": 5,
        }]

    as_melee = built_attacks[0]["as"] if built_attacks else level * 5 + 20

    roam_pct      = scalars.get("roam_chance", 20)
    wander_chance = float(roam_pct) / 100.0

    # Deduplicate spawn / roam rooms
    seen = set()
    unique_spawn = []
    for r in spawn_rooms:
        if isinstance(r, int) and r not in seen:
            seen.add(r)
            unique_spawn.append(r)

    seen2 = set()
    unique_roam = []
    for r in roam_rooms:
        if isinstance(r, int) and r not in seen2:
            seen2.add(r)
            unique_roam.append(r)

    skin_val = scalars.get("skin", None)
    if skin_val == "":
        skin_val = None

    template = {
        "template_id":      template_id,
        "name":             name,
        "article":          article,
        "level":            level,
        "hp":               int(scalars.get("hp_base", 40)),
        "hp_variance":      int(scalars.get("hp_variance", 5)),
        "as_melee":         as_melee,
        "ds_melee":         int(scalars.get("ds_melee", 0)),
        "ds_ranged":        int(scalars.get("ds_melee", 0)),
        "ds_bolt":          int(scalars.get("ds_bolt", 0)),
        "td":               int(scalars.get("td_spiritual", level * 3)),
        "udf":              int(scalars.get("udf", 0)),
        "armor_asg":        int(scalars.get("armor_asg", 1)),
        "armor_natural":    bool(scalars.get("armor_natural", True)),
        "cva":              0,
        "damage_type":      built_attacks[0]["damage_type"] if built_attacks else "crush",
        "body_type":        scalars.get("body_type", "biped"),
        "family":           scalars.get("family", ""),
        "classification":   scalars.get("classification", "living"),
        "description":      scalars.get("description", ""),
        "attacks":          built_attacks,
        "spells":           spells_raw,
        "abilities":        abilities,
        "immune":           immune,
        "resist":           resist,
        "special_loot":     special_loot,
        "skin":             skin_val,
        "treasure": {
            "coins": bool(scalars.get("loot_coins", True)),
            "gems":  bool(scalars.get("loot_gems",  True)),
            "magic": bool(scalars.get("loot_magic", True)),
            "boxes": bool(scalars.get("loot_boxes", True)),
        },
        "decay_seconds":    int(scalars.get("decay_seconds", 300)),
        "crumbles":         bool(scalars.get("crumbles", False)),
        "decay_message":    scalars.get("decay_message", ""),
        "spawn_rooms":      unique_spawn,
        "wander_rooms":     unique_roam,
        "respawn_time":     int(scalars.get("respawn_seconds", 300)),
        "max_count":        int(scalars.get("max_count", 3)),
        "aggressive":       True,
        "wander_chance":    wander_chance,
        "pursue_chance":    0.3,
    }

    return template


# ── Directory scanner ─────────────────────────────────────────────────────────

def load_all_mob_luas(scripts_path: str) -> dict:
    """
    Walk scripts/zones/<zone>/mobs/*.lua for every zone and load all mob files.

    When the same creature name appears in multiple zones (e.g. cobra in both
    Solhaven and Wehnimer's Landing), the spawn_rooms, roam_rooms, and
    max_count are MERGED so the creature spawns in all intended areas.
    Combat stats come from the first file loaded (they should be identical
    for same-name creatures).

    Returns:
        dict mapping template_id -> template dict
        (ready to merge into CREATURE_TEMPLATES)
    """
    templates    = {}
    merged_count = 0
    zones_path   = os.path.join(scripts_path, "zones")

    if not os.path.isdir(zones_path):
        log.warning("Zones directory not found: %s", zones_path)
        return templates

    for zone_slug in sorted(os.listdir(zones_path)):
        zone_path = os.path.join(zones_path, zone_slug)
        if not os.path.isdir(zone_path):
            continue

        mobs_path = os.path.join(zone_path, "mobs")
        if not os.path.isdir(mobs_path):
            continue

        zone_count = 0
        for fname in sorted(os.listdir(mobs_path)):
            if not fname.endswith(".lua"):
                continue
            fpath = os.path.join(mobs_path, fname)
            tmpl  = parse_mob_lua(fpath)
            if tmpl is None:
                continue
            tid = tmpl["template_id"]

            if tid in templates:
                # Same creature in a different zone — merge rooms, don't skip
                existing = templates[tid]

                existing_spawn  = set(existing.get("spawn_rooms", []))
                new_spawn       = [r for r in tmpl.get("spawn_rooms", []) if r not in existing_spawn]
                existing["spawn_rooms"] = existing.get("spawn_rooms", []) + new_spawn

                existing_wander = set(existing.get("wander_rooms", []))
                new_wander      = [r for r in tmpl.get("wander_rooms", []) if r not in existing_wander]
                existing["wander_rooms"] = existing.get("wander_rooms", []) + new_wander

                existing["max_count"] = existing.get("max_count", 3) + tmpl.get("max_count", 3)

                merged_count += 1
                log.info(
                    "  Merged '%s' from zone '%s' (+%d spawn rooms, +%d roam rooms, +%d max_count)",
                    tid, zone_slug, len(new_spawn), len(new_wander), tmpl.get("max_count", 3)
                )
                zone_count += 1
                continue

            templates[tid] = tmpl
            zone_count += 1

        if zone_count:
            log.info("  Loaded %d mob templates from zone '%s'", zone_count, zone_slug)

    if merged_count:
        log.info("Lua mob loader: %d creatures merged from multiple zones", merged_count)
    log.info("Lua mob loader: %d total creature templates loaded", len(templates))
    return templates
