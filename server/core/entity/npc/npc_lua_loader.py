"""
npc_lua_loader.py
-----------------
Scans scripts/npcs/*.lua (flat — no subfolders by design) and parses each
NPC Lua file into a Python template dict that NPCManager understands.

No Lua runtime is used here — this is a fast regex/text parser that reads
the data fields.  Hook functions (on_load, on_player_talk, etc.) are noted
as present/absent but not executed; they run via the Lua engine at runtime.

Parsed fields:
    NPC.template_id        -> "template_id"
    NPC.name               -> "name"
    NPC.article            -> "article"
    NPC.title              -> "title"
    NPC.description        -> "description"
    NPC.home_room_id       -> "room_id" and "home_room_id"

    -- capabilities (all bool)
    NPC.can_combat / can_shop / can_wander / can_emote / can_chat
    NPC.can_loot / is_guild / is_quest / is_house / is_bot / is_invasion

    -- combat
    NPC.level / hp / as_melee / ds_melee / ds_ranged / td
    NPC.armor_asg / body_type / aggressive / unkillable / respawn_seconds
    NPC.attacks             -> "attacks" list of dicts

    -- shop
    NPC.shop_id             -> "shop_id"

    -- wander
    NPC.patrol_rooms        -> "patrol_rooms"
    NPC.wander_chance       -> "wander_chance"
    NPC.move_interval       -> "move_interval"

    -- shift system
    NPC.shift_id / shift_phase / spawn_at_start

    -- rare spawn
    NPC.rare_spawn / spawn_chance

    -- dialogue
    NPC.dialogues           -> "dialogues" dict
    NPC.greeting            -> "greeting"

    -- emotes
    NPC.ambient_emotes      -> "ambient_emotes"
    NPC.ambient_chance / emote_cooldown

    -- chat
    NPC.chat_lines          -> "chat_lines"
    NPC.chat_interval       -> "chat_interval"
    NPC.chat_chance         -> "chat_chance"

    -- loot
    NPC.loot_silver / loot_gems / loot_items / loot_radius

    -- guild
    NPC.guild_id            -> "guild_id"

    -- bot
    NPC.bot_hunt / bot_hunt_rooms / bot_rest_room / bot_hp_flee / bot_chat_world

    -- invasion
    NPC.invasion_zone / invasion_side

    -- hooks present (list of strings)
    "hooks"                 -> ["on_load", "on_player_talk", ...]
"""

import os
import re
import logging

log = logging.getLogger(__name__)

# Known capability flags
_CAPABILITY_KEYS = {
    "can_combat", "can_shop", "can_wander", "can_emote", "can_chat",
    "can_loot", "is_guild", "is_quest", "is_house", "is_bot", "is_invasion",
}

# Hook function names the engine supports
_KNOWN_HOOKS = {
    "on_load", "on_player_enter", "on_player_talk", "on_combat_start",
    "on_combat_victory", "on_death", "on_tick", "on_invasion",
    "on_loot", "on_guild_rank_up",
}

# Mirrors mob loader attack verb table for NPC combat
_ATTACK_VERBS = {
    "claw":         ("rakes you with its claws",         "rakes {target} with its claws",         "slash"),
    "bite":         ("lunges at you with snapping jaws", "lunges at {target} with snapping jaws", "puncture"),
    "broadsword":   ("swings a broadsword at you",       "swings a broadsword at {target}",       "slash"),
    "longsword":    ("swings a longsword at you",        "swings a longsword at {target}",        "slash"),
    "dagger":       ("jabs a dagger at you",             "jabs a dagger at {target}",             "puncture"),
    "scimitar":     ("slashes a scimitar at you",        "slashes a scimitar at {target}",        "slash"),
    "spear":        ("thrusts a spear at you",           "thrusts a spear at {target}",           "puncture"),
    "mace":         ("smashes a mace at you",            "smashes a mace at {target}",            "crush"),
    "staff":        ("strikes you with a staff",         "strikes {target} with a staff",         "crush"),
    "closed_fist":  ("strikes you with a closed fist",   "strikes {target} with a closed fist",  "crush"),
    "kick":         ("kicks you",                        "kicks {target}",                        "crush"),
    "punch":        ("punches you",                      "punches {target}",                      "crush"),
}
_DEFAULT_VERB = ("attacks you", "attacks {target}", "crush")


def _verb_for(attack_type: str, damage_type: str = None):
    entry = _ATTACK_VERBS.get(attack_type.lower(), _DEFAULT_VERB)
    eff_dt = damage_type if damage_type else entry[2]
    return entry[0], entry[1], eff_dt


# ── Inline block guard (same as mob loader) ───────────────────────────────────

def _is_inline_block(line: str) -> bool:
    stripped = line.strip()
    opens  = stripped.count("{")
    closes = stripped.count("}")
    return opens > 0 and opens == closes


# ── Parsers ───────────────────────────────────────────────────────────────────

def _parse_string_list_block(lines, start_idx):
    """Parse { "a", "b", ... } into a list of strings."""
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


def _parse_int_list_block(lines, start_idx):
    """Parse { 1234, 5678, ... } into a list of ints."""
    result = []
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("--"):
            continue
        if "--" in line:
            line = line[:line.index("--")].strip()
        if "}" in line and "=" not in line:
            break
        for m in re.finditer(r'\b(\d+)\b', line):
            result.append(int(m.group(1)))
    return result, i


def _parse_attacks_block(lines, start_idx):
    """Parse NPC.attacks = { { type=..., as=..., damage_type=... }, ... }"""
    attacks = []
    i = start_idx
    depth = 1
    current = {}

    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("--"):
            continue

        opens  = line.count("{")
        closes = line.count("}")
        depth += opens

        if opens and depth >= 2:
            for pair in re.finditer(r'(\w+)\s*=\s*(".*?"|\'.*?\'|\d+)', line):
                k, v = pair.group(1), pair.group(2)
                if v.startswith(('"', "'")):
                    current[k] = v[1:-1]
                else:
                    try:
                        current[k] = int(v)
                    except ValueError:
                        current[k] = v

        depth -= closes

        if closes and current:
            attacks.append(current)
            current = {}

        if depth <= 0:
            break

    return attacks, i


def _parse_dialogues_block(lines, start_idx):
    """
    Parse NPC.dialogues = { keyword = "response", ... }
    Keys are lowercased. Values are the quoted response strings.
    Multi-line values are joined with a space.
    """
    result = {}
    i = start_idx
    depth = 1
    current_key = None
    current_val = []

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        i += 1
        if not line or line.startswith("--"):
            continue

        opens  = line.count("{")
        closes = line.count("}")
        depth += opens - closes

        if depth <= 0:
            # Flush any pending value
            if current_key and current_val:
                result[current_key] = " ".join(current_val).strip()
            break

        # Strip inline comments
        if "--" in line:
            line = line[:line.index("--")].strip()

        # key = "value" on one line
        m = re.match(r'^(\w+)\s*=\s*"(.*)"[,]?\s*$', line)
        if m:
            if current_key and current_val:
                result[current_key] = " ".join(current_val).strip()
            current_key = m.group(1).lower()
            current_val = [m.group(2)]
            continue

        # key = "start of multi-line value...
        m = re.match(r'^(\w+)\s*=\s*"(.*)', line)
        if m and '"' not in line[line.index('"') + 1:]:
            if current_key and current_val:
                result[current_key] = " ".join(current_val).strip()
            current_key = m.group(1).lower()
            current_val = [m.group(2)]
            continue

        # Continuation of a multi-line value
        if current_key:
            # Check if this line closes the string
            if line.endswith('",') or line.endswith('"'):
                current_val.append(line.rstrip('",').rstrip('"'))
                result[current_key] = " ".join(current_val).strip()
                current_key = None
                current_val = []
            else:
                current_val.append(line)

    return result, i


# ── Main file parser ──────────────────────────────────────────────────────────

def parse_npc_lua(filepath: str) -> dict:
    """
    Parse a single NPC Lua file into a Python template dict.
    Returns None if parsing fails or the file has no template_id.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    except OSError as e:
        log.error("Cannot open NPC file %s: %s", filepath, e)
        return None

    lines = [l.rstrip("\r\n") for l in raw_lines]
    scalars = {}
    attacks_raw  = []
    patrol_rooms = []
    bot_hunt_rooms = []
    ambient_emotes = []
    chat_lines   = []
    dialogues    = {}
    hooks_found  = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1

        if not line or line.startswith("--"):
            continue

        # ── Hook detection ────────────────────────────────────────────────────
        # function NPC:on_xxx()   or   function NPC:on_xxx(...)
        m = re.match(r'^function\s+NPC:(\w+)\s*\(', line)
        if m:
            hook = m.group(1)
            if hook in _KNOWN_HOOKS:
                hooks_found.append(hook)
            continue

        # ── Block dispatchers ─────────────────────────────────────────────────
        if "NPC.attacks" in line and "{" in line:
            if _is_inline_block(line):
                attacks_raw = []
            else:
                attacks_raw, i = _parse_attacks_block(lines, i)
            continue

        if "NPC.patrol_rooms" in line and "{" in line:
            if _is_inline_block(line):
                patrol_rooms = [int(x) for x in re.findall(r'\d+', line)]
            else:
                patrol_rooms, i = _parse_int_list_block(lines, i)
            continue

        if "NPC.bot_hunt_rooms" in line and "{" in line:
            if _is_inline_block(line):
                bot_hunt_rooms = [int(x) for x in re.findall(r'\d+', line)]
            else:
                bot_hunt_rooms, i = _parse_int_list_block(lines, i)
            continue

        if "NPC.ambient_emotes" in line and "{" in line:
            if _is_inline_block(line):
                ambient_emotes = re.findall(r'"([^"]+)"', line)
            else:
                ambient_emotes, i = _parse_string_list_block(lines, i)
            continue

        if "NPC.chat_lines" in line and "{" in line:
            if _is_inline_block(line):
                chat_lines = re.findall(r'"([^"]+)"', line)
            else:
                chat_lines, i = _parse_string_list_block(lines, i)
            continue

        if "NPC.dialogues" in line and "{" in line:
            if _is_inline_block(line):
                # Inline: NPC.dialogues = { default = "..." }
                m2 = re.search(r'default\s*=\s*"([^"]+)"', line)
                if m2:
                    dialogues = {"default": m2.group(1)}
            else:
                dialogues, i = _parse_dialogues_block(lines, i)
            continue

        # ── Scalar NPC.key = value ────────────────────────────────────────────
        m = re.match(r'^NPC\.(\w+)\s*=\s*(.+)$', line)
        if not m:
            continue
        key = m.group(1)
        val = m.group(2).strip().rstrip(",").strip()

        # Strip inline comment
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
        elif val.lower() == "nil":
            scalars[key] = None
        else:
            try:
                scalars[key] = int(val)
            except ValueError:
                try:
                    scalars[key] = float(val)
                except ValueError:
                    scalars[key] = val

    # ── Validate ──────────────────────────────────────────────────────────────
    template_id = scalars.get("template_id", "")
    if not template_id or template_id == "npc_base":
        log.debug("NPC file %s skipped (no template_id or is base template)", filepath)
        return None

    name = scalars.get("name", "")
    if not name:
        log.warning("NPC file %s has no name, skipping", filepath)
        return None

    # ── Build attacks ─────────────────────────────────────────────────────────
    level = int(scalars.get("level", 1))
    built_attacks = []
    for atk in attacks_raw:
        atype = atk.get("type", "closed_fist")
        aas   = int(atk.get("as", level * 5 + 30))
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

    # Default unarmed attack for combat NPCs with no attacks block
    can_combat = bool(scalars.get("can_combat", False))
    if can_combat and not built_attacks:
        built_attacks = [{
            "name":        "closed_fist",
            "as":          level * 5 + 30,
            "damage_type": "crush",
            "verb_first":  "strikes you",
            "verb_third":  "strikes {target}",
            "roundtime":   5,
        }]

    # ── Derive article from name if not set ───────────────────────────────────
    article = scalars.get("article", "")
    if not article:
        article = "an" if name[0].lower() in "aeiou" else "a"

    # ── Deduplicate room lists ────────────────────────────────────────────────
    seen = set()
    unique_patrol = []
    for r in patrol_rooms:
        if isinstance(r, int) and r not in seen:
            seen.add(r)
            unique_patrol.append(r)

    seen2 = set()
    unique_bot_hunt = []
    for r in bot_hunt_rooms:
        if isinstance(r, int) and r not in seen2:
            seen2.add(r)
            unique_bot_hunt.append(r)

    # ── Assemble template ─────────────────────────────────────────────────────
    home_room = int(scalars.get("home_room_id", 0))
    template = {
        # Identity
        "template_id":    template_id,
        "name":           name,
        "article":        article,
        "title":          scalars.get("title", ""),
        "description":    scalars.get("description", "You see nothing unusual."),
        "room_id":        home_room,
        "home_room_id":   home_room,
        "lua_file":       filepath,
        "lua_module":     f"npcs/{os.path.splitext(os.path.basename(filepath))[0]}",

        # Capabilities (all booleans)
        "can_combat":     bool(scalars.get("can_combat",  False)),
        "can_shop":       bool(scalars.get("can_shop",    False)),
        "can_wander":     bool(scalars.get("can_wander",  False)),
        "can_emote":      bool(scalars.get("can_emote",   False)),
        "can_chat":       bool(scalars.get("can_chat",    False)),
        "can_loot":       bool(scalars.get("can_loot",    False)),
        "is_guild":       bool(scalars.get("is_guild",    False)),
        "is_quest":       bool(scalars.get("is_quest",    False)),
        "is_house":       bool(scalars.get("is_house",    False)),
        "is_bot":         bool(scalars.get("is_bot",      False)),
        "is_invasion":    bool(scalars.get("is_invasion", False)),

        # Combat stats
        "level":          level,
        "hp":             int(scalars.get("hp",        100)),
        "as_melee":       int(scalars.get("as_melee",  50)),
        "ds_melee":       int(scalars.get("ds_melee",  30)),
        "ds_ranged":      int(scalars.get("ds_ranged", 20)),
        "td":             int(scalars.get("td",        10)),
        "armor_asg":      int(scalars.get("armor_asg", 5)),
        "body_type":      scalars.get("body_type", "biped"),
        "aggressive":     bool(scalars.get("aggressive",   False)),
        "unkillable":     bool(scalars.get("unkillable",   False)),
        "respawn_seconds":int(scalars.get("respawn_seconds", 600)),
        "attacks":        built_attacks,

        # Shop
        "shop_id":        scalars.get("shop_id", None),
        "role":           "shopkeeper" if scalars.get("can_shop") else scalars.get("role", "townsfolk"),

        # Wander / patrol
        "patrol_rooms":   unique_patrol,
        "wander_chance":  float(scalars.get("wander_chance", 0.0)),
        "move_interval":  int(scalars.get("move_interval", 30)),

        # Shift system
        "shift_id":       scalars.get("shift_id", None),
        "shift_phase":    int(scalars.get("shift_phase", 0)),
        "spawn_at_start": bool(scalars.get("spawn_at_start", True)),

        # Rare spawn
        "rare_spawn":     bool(scalars.get("rare_spawn",   False)),
        "spawn_chance":   float(scalars.get("spawn_chance", 1.0)),

        # Dialogue
        "dialogues":      dialogues,
        "greeting":       scalars.get("greeting", None),

        # Emotes
        "ambient_emotes": ambient_emotes,
        "ambient_chance": float(scalars.get("ambient_chance", 0.03)),
        "emote_cooldown": int(scalars.get("emote_cooldown", 45)),

        # Chat
        "chat_lines":     chat_lines,
        "chat_interval":  int(scalars.get("chat_interval", 120)),
        "chat_chance":    float(scalars.get("chat_chance", 0.12)),

        # Loot
        "loot_silver":    bool(scalars.get("loot_silver", True)),
        "loot_gems":      bool(scalars.get("loot_gems",   False)),
        "loot_items":     bool(scalars.get("loot_items",  False)),
        "loot_radius":    int(scalars.get("loot_radius",  0)),

        # Guild
        "guild_id":       scalars.get("guild_id", None),

        # Bot
        "bot_hunt":       bool(scalars.get("bot_hunt",     False)),
        "bot_hunt_rooms": unique_bot_hunt,
        "bot_rest_room":  int(scalars.get("bot_rest_room", 0)),
        "bot_hp_flee":    float(scalars.get("bot_hp_flee", 0.25)),
        "bot_chat_world": bool(scalars.get("bot_chat_world", False)),

        # Invasion
        "invasion_zone":  scalars.get("invasion_zone", None),
        "invasion_side":  scalars.get("invasion_side", "enemy"),

        # Hook manifest
        "hooks":          hooks_found,
    }

    return template


# ── Directory scanner ─────────────────────────────────────────────────────────

def load_all_npc_luas(scripts_path: str) -> dict:
    """
    Scan scripts/npcs/*.lua (flat) and parse every NPC file.

    Returns:
        dict mapping template_id -> template dict
    """
    npcs_path = os.path.join(scripts_path, "npcs")
    templates = {}

    if not os.path.isdir(npcs_path):
        log.info("NPC Lua directory not found: %s — no Lua NPCs loaded", npcs_path)
        return templates

    count = 0
    for fname in sorted(os.listdir(npcs_path)):
        if not fname.endswith(".lua"):
            continue
        if fname == "npc_base.lua":
            continue  # skip the template itself

        fpath = os.path.join(npcs_path, fname)
        tmpl  = parse_npc_lua(fpath)
        if tmpl is None:
            continue

        tid = tmpl["template_id"]
        if tid in templates:
            log.warning("Duplicate NPC template_id '%s' in %s — skipping", tid, fname)
            continue

        templates[tid] = tmpl
        count += 1
        caps = [k for k in (
            "can_combat", "can_shop", "can_wander", "can_emote",
            "can_chat", "can_loot", "is_guild", "is_quest",
            "is_house", "is_bot", "is_invasion",
        ) if tmpl.get(k)]
        log.debug(
            "  NPC '%s' (%s) — caps: [%s] hooks: [%s]",
            tid, tmpl["name"],
            ", ".join(caps) if caps else "none",
            ", ".join(tmpl.get("hooks", [])),
        )

    log.info("NPC Lua loader: %d NPC templates loaded from %s", count, npcs_path)
    return templates
