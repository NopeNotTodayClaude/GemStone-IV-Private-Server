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

import copy
import json
import os
import re
import logging
from collections import Counter

from lupa import LuaRuntime  # type: ignore

log = logging.getLogger(__name__)

_AREA_ROOM_FILTERS = {
    "Atoll": {"images": {"kf-atoll-1652294074.jpg"}},
    "Czeroth Labyrinth": {"images": {"en-zul_czeroth.png"}},
    "Hinterwilds": {"images": {"imt-Hinterwilds-1651886165.jpg"}},
    "Kharam Dzu": {"title_contains": {"kharam dzu"}},
    "Moonsedge": {"images": {"imt-Moonsedge-1770317665.png"}},
    "Old Ta'Faendryl": {"images": {"en-old_ta_faendryl-1716923763.png"}},
    "Ruined Temple": {"images": {"ti-nelemar-1262373036.png"}},
    "Sailor's Grief": {"images": {"Sailors_Grief.jpg"}},
    "Sanctum": {"images": {"SanctumMap-Eiadh-1643825243.png"}},
    "Scatter": {"images": {"imt-scatter-1264234799.png"}},
    "Ship Graveyard": {"title_contains": {"the mageborn", "the kyusharu", "the tonbury", "spicers sea", "sailors grief"}},
    "Thanatoph": {"images": {"wl-stronghold-1264234799.png"}},
    "The Contempt": {"title_contains": {"the contempt"}},
    "The Broken Lands": {"images": {"wl-broken-1264234799.png"}},
    "The Citadel": {"images": {"rr-citadel-1717856937.png"}},
    "The Hive": {"images": {"en-zul_logoth_the_hive-1702229165.png"}},
    "The Rift": {"images": {"imt-rift-1554575848.png"}},
}

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
    "longbow":          ("looses an arrow at you",            "looses an arrow at {target}",            "puncture"),
    "shortbow":         ("looses an arrow at you",            "looses an arrow at {target}",            "puncture"),
    "crossbow":         ("fires a bolt at you",               "fires a bolt at {target}",               "puncture"),
    "shortsword":       ("slashes a shortsword at you",       "slashes a shortsword at {target}",       "slash"),
    "falchion":         ("sweeps a falchion at you",          "sweeps a falchion at {target}",          "slash"),
    "waraxe":           ("hacks a waraxe at you",             "hacks a waraxe at {target}",             "slash"),
    "warhammer":        ("hammers a warhammer into you",      "hammers a warhammer into {target}",      "crush"),
    "club":             ("clubs you brutally",                "clubs {target} brutally",                "crush"),
    "fang":             ("sinks curved fangs into you",       "sinks curved fangs into {target}",       "puncture"),
    "talon":            ("slashes you with vicious talons",   "slashes {target} with vicious talons",   "slash"),
    "horn":             ("gouges you with a horned thrust",   "gouges {target} with a horned thrust",   "puncture"),
    "shadow_bite":      ("bites through you with chill shadow", "bites through {target} with chill shadow", "puncture"),
    "shadow_claw":      ("rakes you with shadowy claws",      "rakes {target} with shadowy claws",      "slash"),
    "slam_fist":        ("smashes a heavy fist into you",     "smashes a heavy fist into {target}",     "crush"),
    "tentacle":         ("lashes you with a writhing tentacle","lashes {target} with a writhing tentacle","crush"),
    "beak":             ("jabs you with a stabbing beak",     "jabs {target} with a stabbing beak",     "puncture"),
    "peck":             ("pecks savagely at you",             "pecks savagely at {target}",             "puncture"),
    "web":              ("spits webbing at you",              "spits webbing at {target}",              "crush"),
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

ATTACK_VERBS.update({
    "attack": ATTACK_VERBS["closed_fist"],
    "arm": ATTACK_VERBS["closed_fist"],
    "arrow": ATTACK_VERBS["longbow"],
    "ball_and_chain": ATTACK_VERBS["morning_star"],
    "battle_axe": ATTACK_VERBS["waraxe"],
    "bite_attack": ATTACK_VERBS["bite"],
    "bite_enraged": ATTACK_VERBS["bite"],
    "branch_rake": ATTACK_VERBS["claw"],
    "charge_attack": ATTACK_VERBS["charge"],
    "claw_attack": ATTACK_VERBS["claw"],
    "claw_enraged": ATTACK_VERBS["claw"],
    "claidhmore": ATTACK_VERBS["two_handed_sword"],
    "closed_fist_closed_fist_wizards": ATTACK_VERBS["closed_fist"],
    "cudgel": ATTACK_VERBS["club"],
    "dart": ("flicks a dart at you", "flicks a dart at {target}", "puncture"),
    "dhara_dhara_rogues": ATTACK_VERBS["closed_fist"],
    "dual_armrake": ATTACK_VERBS["claw"],
    "ensnare_attack": ATTACK_VERBS["ensnare"],
    "ensnare_attack_ensnare": ATTACK_VERBS["ensnare"],
    "espadon": ATTACK_VERBS["two_handed_sword"],
    "fist": ATTACK_VERBS["closed_fist"],
    "flamberge": ATTACK_VERBS["two_handed_sword"],
    "flail": ATTACK_VERBS["morning_star"],
    "giant_bee_stinger": ATTACK_VERBS["sting"],
    "greatsword": ATTACK_VERBS["two_handed_sword"],
    "greataxe": ATTACK_VERBS["waraxe"],
    "hairy_hand": ATTACK_VERBS["claw"],
    "hatchet": ATTACK_VERBS["handaxe"],
    "hammer": ATTACK_VERBS["warhammer"],
    "hammer_of_kai": ATTACK_VERBS["warhammer"],
    "heavy_crossbow": ATTACK_VERBS["crossbow"],
    "ice_pick": ATTACK_VERBS["military_pick"],
    "impale": ATTACK_VERBS["gore"],
    "impale_attack": ATTACK_VERBS["gore"],
    "jeddart_axe": ATTACK_VERBS["handaxe"],
    "kaskara": ATTACK_VERBS["broadsword"],
    "lance": ATTACK_VERBS["spear"],
    "lash": ("lashes you with a snapping strike", "lashes {target} with a snapping strike", "slash"),
    "leather_whip": ("lashes you with a leather whip", "lashes {target} with a leather whip", "slash"),
    "length_of_rusted_chain": ATTACK_VERBS["morning_star"],
    "maul": ATTACK_VERBS["warhammer"],
    "main_gauche": ATTACK_VERBS["dagger"],
    "massive_icicle": ATTACK_VERBS["spear"],
    "melee_stab": ATTACK_VERBS["dagger"],
    "military_fork": ATTACK_VERBS["spear"],
    "moon_axe": ATTACK_VERBS["waraxe"],
    "pincer_attack": ATTACK_VERBS["pincer"],
    "pound_attack": ATTACK_VERBS["pound"],
    "pound_double_attack": ATTACK_VERBS["pound"],
    "quarterstaff": ATTACK_VERBS["staff"],
    "rapier": ATTACK_VERBS["dagger"],
    "ranged_frost_covered_crystalline_flower": ("launches a frost-rimed blossom at you", "launches a frost-rimed blossom at {target}", "puncture"),
    "ranged_frosty_seed": ("spits a frosty seed at you", "spits a frosty seed at {target}", "puncture"),
    "rock_hurled": ("hurls a jagged rock at you", "hurls a jagged rock at {target}", "crush"),
    "root_lash": ("lashes you with a whipping root", "lashes {target} with a whipping root", "slash"),
    "root_slam": ATTACK_VERBS["slam"],
    "runestaff": ATTACK_VERBS["staff"],
    "scaling_fork": ATTACK_VERBS["spear"],
    "scythe": ATTACK_VERBS["falchion"],
    "short_sword": ATTACK_VERBS["shortsword"],
    "sledgehammer": ATTACK_VERBS["warhammer"],
    "small_glistening_thorn": ATTACK_VERBS["sting"],
    "stalagmite": ATTACK_VERBS["spear"],
    "stinger_attack": ATTACK_VERBS["sting"],
    "strike": ATTACK_VERBS["closed_fist"],
    "stomp_attack": ATTACK_VERBS["stomp"],
    "stomp_attack_stomp": ATTACK_VERBS["stomp"],
    "tail_swing": ATTACK_VERBS["tail_sweep"],
    "thrown": ("hurls a missile at you", "hurls a missile at {target}", "puncture"),
    "thrown_rock": ("hurls a heavy rock at you", "hurls a heavy rock at {target}", "crush"),
    "tongue_strike": ("lashes at you with a snapping tongue", "lashes at {target} with a snapping tongue", "slash"),
    "trident": ATTACK_VERBS["spear"],
    "trunk_slam": ATTACK_VERBS["slam"],
    "tusk_spear": ATTACK_VERBS["gore"],
    "ucs": ATTACK_VERBS["closed_fist"],
    "unarmed_combat": ATTACK_VERBS["closed_fist"],
    "war_mattock": ATTACK_VERBS["military_pick"],
    "war_hammer": ATTACK_VERBS["warhammer"],
    "whip": ("lashes you with a vicious whip", "lashes {target} with a vicious whip", "slash"),
    "wiry_arms": ATTACK_VERBS["closed_fist"],
    "dive": ("dives at you in a tearing rush", "dives at {target} in a tearing rush", "slash"),
})


def _lua_table_to_python(tbl):
    """Recursively convert a Lua table returned by lupa into native Python values."""
    if tbl is None:
        return None
    if hasattr(tbl, "items"):
        items = list(tbl.items())
        if items and all(isinstance(k, int) for k, _ in items):
            return [_lua_table_to_python(v) for _, v in sorted(items, key=lambda row: row[0])]
        return {k: _lua_table_to_python(v) for k, v in items}
    return tbl


def _derive_article(name: str) -> str:
    clean = (name or "").strip()
    if not clean:
        return "a"
    return "an" if clean[0].lower() in "aeiou" else "a"


def _dedupe_int_list(values):
    seen = set()
    out = []
    for value in values or []:
        try:
            ivalue = int(value)
        except Exception:
            continue
        if ivalue in seen:
            continue
        seen.add(ivalue)
        out.append(ivalue)
    return out


def _clean_catalog_description(text: str) -> str:
    cleaned = str(text or "")
    if not cleaned:
        return ""
    cleaned = re.sub(r"__[^_]+__", " ", cleaned)
    cleaned = re.sub(r"\{\{Otheruses[^}]*\}\}", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\{\{TOC[^}]*\}\}", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\{\{[^}]+\}\}", " ", cleaned)
    cleaned = re.sub(r"==+\s*[^=]+?\s*==+", " ", cleaned)
    cleaned = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", cleaned)
    cleaned = re.sub(r"\[\[([^\]]+)\]\]", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _normalize_template(template: dict) -> dict:
    """Ensure a template dict is runtime-safe after file/catalog merging."""
    result = copy.deepcopy(template)
    name = str(result.get("name", "") or "").strip()
    level = int(result.get("level", 1) or 1)
    result["name"] = name
    result["article"] = str(result.get("article") or _derive_article(name))
    result["template_id"] = str(result.get("template_id") or name.lower().replace(" ", "_").replace("'", ""))
    result["level"] = level
    result["hp"] = int(result.get("hp", result.get("hp_base", 40)) or 40)
    result["hp_variance"] = int(result.get("hp_variance", 5) or 5)
    result["ds_melee"] = int(result.get("ds_melee", 0) or 0)
    result["ds_ranged"] = int(result.get("ds_ranged", result.get("ds_melee", 0)) or 0)
    result["ds_bolt"] = int(result.get("ds_bolt", 0) or 0)
    result["td"] = int(result.get("td", result.get("td_spiritual", level * 3)) or (level * 3))
    result["td_spiritual"] = int(result.get("td_spiritual", result["td"]) or result["td"])
    result["td_elemental"] = int(result.get("td_elemental", result["td"]) or result["td"])
    result["udf"] = int(result.get("udf", 0) or 0)
    result["armor_asg"] = int(result.get("armor_asg", 1) or 1)
    result["armor_natural"] = bool(result.get("armor_natural", True))
    result["cva"] = int(result.get("cva", 0) or 0)
    result["body_type"] = str(result.get("body_type", "biped") or "biped")
    result["family"] = str(result.get("family", "") or "")
    result["classification"] = str(result.get("classification", "living") or "living")
    result["description"] = _clean_catalog_description(result.get("description", "") or "")
    result["skin"] = str(result.get("skin", "") or "").strip() or None
    result["special_loot"] = list(result.get("special_loot", []) or [])
    result["spells"] = list(result.get("spells", []) or [])
    result["abilities"] = list(result.get("abilities", []) or [])
    result["immune"] = list(result.get("immune", []) or [])
    result["resist"] = list(result.get("resist", []) or [])
    result["skills"] = list(result.get("skills", []) or [])
    result["spawn_rooms"] = _dedupe_int_list(result.get("spawn_rooms", []))
    result["wander_rooms"] = _dedupe_int_list(result.get("wander_rooms", []))
    result["respawn_time"] = int(result.get("respawn_time", result.get("respawn_seconds", 300)) or 300)
    result["max_count"] = int(result.get("max_count", 3) or 3)
    roam_pct = result.get("roam_chance_pct", None)
    if roam_pct is not None:
        result["wander_chance"] = max(0.0, min(1.0, float(roam_pct) / 100.0))
    else:
        result["wander_chance"] = float(result.get("wander_chance", 0.2) or 0.2)
    result["pursue_chance"] = float(result.get("pursue_chance", 0.3) or 0.3)
    result["aggressive"] = bool(result.get("aggressive", True))
    result["preferred_stance"] = str(result.get("preferred_stance", "") or "").strip().lower() or None
    result["stance_profile"] = str(result.get("stance_profile", "") or "").strip().lower() or None
    result["treasure"] = {
        "coins": bool((result.get("treasure") or {}).get("coins", result.get("loot_coins", True))),
        "gems": bool((result.get("treasure") or {}).get("gems", result.get("loot_gems", True))),
        "magic": bool((result.get("treasure") or {}).get("magic", result.get("loot_magic", True))),
        "boxes": bool((result.get("treasure") or {}).get("boxes", result.get("loot_boxes", True))),
    }
    attacks = list(result.get("attacks", []) or [])
    built_attacks = []
    for atk in attacks:
        if not isinstance(atk, dict):
            continue
        atype = str(atk.get("name", atk.get("type", "attack")) or "attack")
        aas = int(atk.get("as", result.get("as_melee", level * 5 + 20)) or (level * 5 + 20))
        adt = str(atk.get("damage_type", "") or "")
        vf, vt, eff_dt = _verb_for(atype, adt)
        built_attacks.append({
            "name": atype,
            "as": aas,
            "damage_type": eff_dt,
            "verb_first": str(atk.get("verb_first", vf) or vf),
            "verb_third": str(atk.get("verb_third", vt) or vt),
            "roundtime": int(atk.get("roundtime", 5) or 5),
        })
    if not built_attacks:
        as_melee = int(result.get("as_melee", level * 5 + 20) or (level * 5 + 20))
        built_attacks = [{
            "name": "attack",
            "as": as_melee,
            "damage_type": "crush",
            "verb_first": "attacks you",
            "verb_third": "attacks {target}",
            "roundtime": 5,
        }]
    result["attacks"] = built_attacks
    result["as_melee"] = int(result.get("as_melee", built_attacks[0]["as"]) or built_attacks[0]["as"])
    result["damage_type"] = str(result.get("damage_type", built_attacks[0]["damage_type"]) or built_attacks[0]["damage_type"])
    if not result["skills"]:
        result["skills"] = _infer_creature_skills(result)
    return result


def _infer_creature_skills(result: dict) -> list:
    """Fill generic skill metadata for creatures that have none authored."""
    skills = []

    def add(*names):
        for name in names:
            name = str(name or "").strip().lower()
            if name and name not in skills:
                skills.append(name)

    family = str(result.get("family", "") or "").strip().lower()
    stance_profile = str(result.get("stance_profile", "") or "").strip().lower()
    classification = str(result.get("classification", "") or "").strip().lower()
    has_spells = bool(result.get("spells"))

    if has_spells or stance_profile == "caster":
        add("spell_aiming", "mana_control", "arcane_lore")
    if stance_profile == "ranged":
        add("perception", "ambush", "tracking")
    elif stance_profile == "skirmisher":
        add("perception", "ambush", "survival")
    elif stance_profile == "berserker":
        add("physical_fitness", "combat_maneuvers")
    elif stance_profile == "offensive":
        add("perception", "combat_maneuvers")

    if family in {
        "feline", "canine", "bear", "wolf", "hound", "arachnid", "spider", "bird",
        "deer", "boar", "primate", "rodent", "basilisk", "scorpion", "insect",
        "worm", "reptilian", "lizard", "horse",
    }:
        add("survival", "perception")
    if family in {"feline", "canine", "wolf", "hound", "arachnid", "spider"}:
        add("stalking", "ambush")
    if family in {"troll", "ogre", "giant", "krolvin", "orc", "gnoll", "grutik", "hisskra", "humanoid", "shelfae"}:
        add("physical_fitness", "combat_maneuvers")
    if family in {"wight", "spectre", "ghost", "wraith", "spirit", "skeleton", "zombie", "ghoul"} or classification != "living":
        add("perception", "spiritual_lore")
    if not skills:
        add("perception", "physical_fitness")
    return skills


def _merge_template(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base or {})
    for key, value in (override or {}).items():
        if key in {"base_template", "spawn_from", "roam_from"}:
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            new_dict = copy.deepcopy(merged.get(key) or {})
            new_dict.update(copy.deepcopy(value))
            merged[key] = new_dict
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _scale_numeric(value, ratio: float, minimum: int = None) -> int:
    try:
        scaled = int(round(float(value) * float(ratio)))
    except Exception:
        scaled = int(value or 0)
    if minimum is not None:
        scaled = max(int(minimum), scaled)
    return scaled


def _scale_catalog_template(base: dict, merged: dict, override: dict) -> dict:
    """
    Scale inherited numeric combat fields when a catalog entry clones a base
    template from a different level. Explicit override values always win.
    """
    if not base:
        return merged
    try:
        donor_level = int(base.get("level", 1) or 1)
        new_level = int(merged.get("level", donor_level) or donor_level)
    except Exception:
        return merged
    if donor_level <= 0 or donor_level == new_level:
        return merged

    ratio = max(0.40, min(3.50, float(new_level) / float(donor_level)))
    scaled = copy.deepcopy(merged)
    explicit = set((override or {}).keys())

    for key, minimum in (
        ("hp", 10),
        ("hp_variance", 1),
        ("as_melee", 5),
        ("ds_melee", 0),
        ("ds_ranged", 0),
        ("ds_bolt", 0),
        ("td", 0),
        ("td_spiritual", 0),
        ("td_elemental", 0),
        ("udf", 0),
    ):
        if key in explicit or key not in base:
            continue
        scaled[key] = _scale_numeric(base.get(key, 0), ratio, minimum)

    if "attacks" not in explicit and isinstance(base.get("attacks"), list):
        scaled_attacks = []
        for atk in copy.deepcopy(base.get("attacks") or []):
            if isinstance(atk, dict) and "as" in atk:
                atk["as"] = _scale_numeric(atk.get("as", 0), ratio, 5)
            scaled_attacks.append(atk)
        scaled["attacks"] = scaled_attacks

    if "spells" not in explicit and isinstance(base.get("spells"), list):
        scaled_spells = []
        for spell in copy.deepcopy(base.get("spells") or []):
            if isinstance(spell, dict):
                if "cs" in spell:
                    spell["cs"] = _scale_numeric(spell.get("cs", 0), ratio, 1)
                if "as" in spell and int(spell.get("as", 0) or 0) > 0:
                    spell["as"] = _scale_numeric(spell.get("as", 0), ratio, 1)
            scaled_spells.append(spell)
        scaled["spells"] = scaled_spells

    return scaled


def _resolve_room_sources(source, templates: dict, key: str):
    if not source:
        return []
    ids = source if isinstance(source, list) else [source]
    rooms = []
    seen = set()
    for template_id in ids:
        donor = templates.get(str(template_id or ""))
        if not donor:
            log.warning("Creature catalog: room source '%s' was not found", template_id)
            continue
        for room_id in donor.get(key, []) or []:
            try:
                room_id = int(room_id)
            except Exception:
                continue
            if room_id in seen:
                continue
            seen.add(room_id)
            rooms.append(room_id)
    return rooms


def _normalize_area_tokens(text: str) -> list[str]:
    normalized = re.sub(r"[^a-z0-9]+", " ", str(text or "").lower().replace("'", ""))
    stopwords = {"the", "of", "and", "a", "an", "to", "in", "on", "at", "mt", "mount"}
    return [token for token in normalized.split() if token and token not in stopwords]


def _load_room_area_index(scripts_path: str) -> list[dict]:
    project_root = os.path.abspath(os.path.join(scripts_path, ".."))
    room_graph_path = os.path.join(project_root, "client", "data", "room_graph.json")
    if not os.path.isfile(room_graph_path):
        log.warning("Creature catalog area resolver: room graph not found at %s", room_graph_path)
        return []
    try:
        with open(room_graph_path, "r", encoding="utf-8-sig") as handle:
            data = json.load(handle) or {}
    except Exception as exc:
        log.error("Creature catalog area resolver failed for %s: %s", room_graph_path, exc, exc_info=True)
        return []

    rooms = []
    for room_id, room in (data.get("rooms") or {}).items():
        try:
            rid = int(room_id)
        except Exception:
            continue
        title = str(room.get("title", "") or "")
        zone_name = str(room.get("zone_name", "") or "")
        location = str(room.get("location", "") or "")
        region_name = str(room.get("region_name", "") or "")
        image = str(room.get("image", "") or "")
        strict_text = " | ".join(part for part in (title, zone_name, location) if part)
        broad_text = " | ".join(part for part in (title, zone_name, location, region_name, image) if part)
        rooms.append({
            "room_id": rid,
            "title": title,
            "zone_name": zone_name,
            "location": location,
            "region_name": region_name,
            "image": image,
            "strict_tokens": set(_normalize_area_tokens(strict_text)),
            "broad_tokens": set(_normalize_area_tokens(broad_text)),
        })
    return rooms


def _apply_area_room_filter(area_name: str, matches: list[dict]) -> list[dict]:
    if not matches:
        return []

    rule = _AREA_ROOM_FILTERS.get(str(area_name or "").strip())
    if rule:
        images = {str(value) for value in (rule.get("images") or set())}
        regions = {str(value) for value in (rule.get("regions") or set())}
        title_contains = {str(value).lower() for value in (rule.get("title_contains") or set())}
        filtered = []
        for room in matches:
            if images and str(room.get("image", "") or "") in images:
                filtered.append(room)
                continue
            if regions and str(room.get("region_name", "") or "") in regions:
                filtered.append(room)
                continue
            if title_contains:
                title_text = str(room.get("title", "") or "").lower()
                zone_text = str(room.get("zone_name", "") or "").lower()
                location_text = str(room.get("location", "") or "").lower()
                joined = " | ".join((title_text, zone_text, location_text))
                if any(token in joined for token in title_contains):
                    filtered.append(room)
                    continue
        if filtered:
            return filtered

    buckets = Counter(
        (str(room.get("region_name", "") or ""), str(room.get("image", "") or ""))
        for room in matches
    )
    non_empty = [(key, count) for key, count in buckets.items() if key != ("", "")]
    non_empty.sort(key=lambda row: (-row[1], row[0]))
    if len(non_empty) >= 2:
        (dominant_key, dominant_count), (_, second_count) = non_empty[0], non_empty[1]
        total = len(matches)
        if dominant_count >= max(8, int(total * 0.60)) and dominant_count >= max(2, second_count * 2):
            filtered = [
                room for room in matches
                if (str(room.get("region_name", "") or ""), str(room.get("image", "") or "")) == dominant_key
            ]
            if filtered:
                return filtered
    return matches


def _resolve_named_areas(area_names, room_index: list[dict]) -> list[int]:
    if not area_names:
        return []
    values = area_names if isinstance(area_names, list) else [area_names]
    room_ids = []
    seen = set()
    for raw_name in values:
        area_name = str(raw_name or "").strip()
        if not area_name:
            continue
        tokens = _normalize_area_tokens(area_name)
        if not tokens:
            continue

        strict_matches = [
            room
            for room in room_index
            if all(token in room["strict_tokens"] for token in tokens)
        ]
        broad_matches = strict_matches or [
            room
            for room in room_index
            if all(token in room["broad_tokens"] for token in tokens)
        ]
        filtered_matches = _apply_area_room_filter(area_name, broad_matches)
        if not filtered_matches:
            log.warning("Creature catalog area '%s' did not resolve to any local wayto rooms", area_name)
            continue
        for room in filtered_matches:
            room_id = int(room["room_id"])
            if room_id in seen:
                continue
            seen.add(room_id)
            room_ids.append(room_id)
    return room_ids


def _iter_creature_catalog_paths(scripts_path: str) -> list[str]:
    data_dir = os.path.join(scripts_path, "data")
    if not os.path.isdir(data_dir):
        return []
    paths = []
    for file_name in os.listdir(data_dir):
        if not file_name.startswith("creature_catalog") or not file_name.endswith(".lua"):
            continue
        paths.append(os.path.join(data_dir, file_name))

    def _catalog_sort_key(path: str):
        name = os.path.basename(path)
        numbers = [int(value) for value in re.findall(r"(\d+)", name)]
        primary = numbers[0] if numbers else 9999
        secondary = numbers[1] if len(numbers) > 1 else primary
        return (primary, secondary, name)

    return sorted(paths, key=_catalog_sort_key)


def _load_creature_catalogs(scripts_path: str, templates: dict):
    catalog_paths = _iter_creature_catalog_paths(scripts_path)
    if not catalog_paths:
        return templates
    room_index = _load_room_area_index(scripts_path)
    total_overrides = 0
    total_creatures = 0
    for catalog_path in catalog_paths:
        templates, override_count, creature_count = _load_creature_catalog_file(catalog_path, templates, room_index)
        total_overrides += override_count
        total_creatures += creature_count
    log.info(
        "Creature catalog loader: applied %d overrides and %d catalog creature entries across %d file(s)",
        total_overrides,
        total_creatures,
        len(catalog_paths),
    )
    return templates


def _load_creature_catalog_file(catalog_path: str, templates: dict, room_index: list[dict]):
    try:
        lua = LuaRuntime(unpack_returned_tuples=True)
        with open(catalog_path, "r", encoding="utf-8") as handle:
            catalog_src = handle.read()
        raw = _lua_table_to_python(lua.execute(catalog_src)) or {}
    except Exception as exc:
        log.error("Creature catalog loader failed for %s: %s", catalog_path, exc, exc_info=True)
        return templates, 0, 0

    overrides = raw.get("overrides") or {}
    for template_id, override in overrides.items():
        if template_id not in templates:
            log.warning("Creature catalog override skipped for unknown template '%s'", template_id)
            continue
        merged = _merge_template(templates[template_id], override)
        if override.get("spawn_areas"):
            merged["spawn_rooms"] = _resolve_named_areas(override.get("spawn_areas"), room_index)
        elif override.get("spawn_from"):
            merged["spawn_rooms"] = _resolve_room_sources(override.get("spawn_from"), templates, "spawn_rooms")
        if override.get("roam_areas"):
            merged["wander_rooms"] = _resolve_named_areas(override.get("roam_areas"), room_index)
        elif override.get("roam_from") or override.get("spawn_from"):
            merged["wander_rooms"] = _resolve_room_sources(override.get("roam_from") or override.get("spawn_from"), templates, "wander_rooms")
        merged["catalog_override"] = True
        templates[template_id] = _normalize_template(merged)

    for entry in raw.get("creatures") or []:
        if not isinstance(entry, dict):
            continue
        template_id = str(entry.get("template_id") or "")
        base_template = str(entry.get("base_template") or "")
        base = templates.get(base_template, {})
        if base_template and not base:
            log.warning("Creature catalog base template '%s' not found for '%s'", base_template, template_id or entry.get("name"))
        merged = _merge_template(base, entry)
        if base_template and base:
            merged = _scale_catalog_template(base, merged, entry)
        if entry.get("spawn_areas"):
            merged["spawn_rooms"] = _resolve_named_areas(entry.get("spawn_areas"), room_index)
        elif entry.get("spawn_from"):
            merged["spawn_rooms"] = _resolve_room_sources(entry.get("spawn_from"), templates, "spawn_rooms")
        elif base_template:
            # No explicit spawn_from — do NOT inherit spawn_rooms from base_template.
            # Catalog entries borrow COMBAT stats from a base, not spawn locations.
            # Zone spawns.lua is the sole authority on where a creature spawns.
            merged["spawn_rooms"] = []
        if entry.get("roam_areas"):
            merged["wander_rooms"] = _resolve_named_areas(entry.get("roam_areas"), room_index)
        elif entry.get("roam_from") or entry.get("spawn_from"):
            merged["wander_rooms"] = _resolve_room_sources(entry.get("roam_from") or entry.get("spawn_from"), templates, "wander_rooms")
        elif base_template:
            # No explicit roam_from/spawn_from — do NOT inherit wander_rooms from base_template.
            merged["wander_rooms"] = []
        normalized = _normalize_template(merged)
        normalized["template_origin"] = "catalog"
        normalized["catalog_base_template"] = base_template or None
        normalized["catalog_spawn_from"] = str(entry.get("spawn_from") or entry.get("roam_from") or "") or None
        normalized["catalog_spawn_areas"] = list(entry.get("spawn_areas", []) or [])
        normalized["source_zone"] = None
        normalized["source_zones"] = []
        normalized["source_files"] = [catalog_path]
        templates[normalized["template_id"]] = normalized

    return templates, len(overrides), len(raw.get("creatures") or [])


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
        "td_spiritual":     int(scalars.get("td_spiritual", level * 3)),
        "td_elemental":     int(scalars.get("td_elemental", scalars.get("td_spiritual", level * 3))),
        "udf":              int(scalars.get("udf", 0)),
        "armor_asg":        int(scalars.get("armor_asg", 1)),
        "armor_natural":    bool(scalars.get("armor_natural", True)),
        "cva":              int(scalars.get("cva", 0)),
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
        "aggressive":       bool(scalars.get("aggressive", True)),
        "wander_chance":    wander_chance,
        "pursue_chance":    float(scalars.get("pursue_chance", 0.3) or 0.3),
        "preferred_stance": str(scalars.get("preferred_stance", "") or "").strip().lower() or None,
        "stance_profile":   str(scalars.get("stance_profile", "") or "").strip().lower() or None,
    }

    return _normalize_template(template)


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
            tmpl["template_origin"] = "authored"
            tmpl["source_zone"] = zone_slug
            tmpl["source_zones"] = [zone_slug]
            tmpl["source_files"] = [fpath]

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
                existing_zones = set(existing.get("source_zones", []) or [])
                existing_zones.update(tmpl.get("source_zones", []) or [])
                existing["source_zones"] = sorted(existing_zones)
                existing_files = list(existing.get("source_files", []) or [])
                for path in tmpl.get("source_files", []) or []:
                    if path not in existing_files:
                        existing_files.append(path)
                existing["source_files"] = existing_files

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

    templates = _load_creature_catalogs(scripts_path, templates)

    if merged_count:
        log.info("Lua mob loader: %d creatures merged from multiple zones", merged_count)
    log.info("Lua mob loader: %d total creature templates loaded", len(templates))
    return templates
