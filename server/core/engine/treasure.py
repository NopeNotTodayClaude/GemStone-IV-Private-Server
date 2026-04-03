"""
GemStone IV Treasure Generation Engine

Generates loot from creature kills using real item templates from the DB.
Matches GS4 mechanics: coins, gems, boxes, skins, magic items based on
creature level and treasure flags.
"""

import random
import logging

log = logging.getLogger(__name__)


# Gem tiers by creature level range -> value range
GEM_VALUE_TIERS = {
    (1, 5): (10, 150),
    (6, 10): (50, 400),
    (11, 15): (100, 800),
    (16, 20): (200, 1500),
    (21, 30): (500, 2500),
}

# Container types by creature level range
BOX_TIERS = {
    (1, 5): ["wooden coffer", "dented iron box", "ornate brass box"],
    (6, 10): ["wooden coffer", "iron coffer", "small chest", "ornate brass box"],
    (11, 15): ["iron coffer", "small chest", "metal strongbox", "small steel lockbox"],
    (16, 20): ["metal strongbox", "medium chest", "small steel lockbox", "heavy steel trunk"],
    (21, 30): ["enruned strongbox", "large chest", "heavy steel trunk", "mithril coffer"],
}

# Lock difficulty scaling per creature level
LOCK_DIFFICULTY_BASE = 5   # per creature level -- calibrated for ranks*3 skill formula
                            # GS4 uses 15 but their skill values are 3-4x higher per rank

ABILITY_SPECIAL_LOOT = {
    "crystal_core_drop": "a crystal core",
    "essence_shard_drop": "an essence shard",
    "drops_pale_water_sapphire": "a pale water sapphire",
}


def _get_tier_value(tiers, level):
    """Look up a value from a level-range tier dict."""
    for (low, high), value in tiers.items():
        if low <= level <= high:
            return value
    # Default: use highest tier
    return list(tiers.values())[-1]


def generate_coins(creature_level):
    """Generate coin drop amount based on creature level."""
    base = creature_level * 15
    variance = creature_level * 10
    return max(1, random.randint(base - variance, base + variance + 20))


def generate_gem(db, creature_level):
    """
    Pick a random gem template from the DB appropriate for creature level.
    Returns item dict or None.
    """
    min_val, max_val = _get_tier_value(GEM_VALUE_TIERS, creature_level)

    try:
        # Query gem templates within value range
        query = """
            SELECT id, name, short_name, noun, value, description, gem_family
            FROM items
            WHERE item_type = 'gem'
              AND is_template = 1
              AND value >= %s AND value <= %s
            ORDER BY RAND()
            LIMIT 1
        """
        result = db.execute_query(query, (min_val, max_val))
        if result and len(result) > 0:
            row = result[0]
            return {
                "item_id": row[0],
                "name": row[1],
                "short_name": row[2],
                "noun": row[3],
                "value": row[4],
                "description": row[5],
                "item_type": "gem",
            }
    except Exception as e:
        log.warning(f"Failed to query gem template: {e}")

    return None


def generate_box(db, creature_level, server=None):
    """
    Pick a random treasure container appropriate for creature level.
    Returns item dict with lock_difficulty, trap info, and contents set, or None.
    """
    box_names = _get_tier_value(BOX_TIERS, creature_level)
    chosen_name = random.choice(box_names)

    lock_diff  = creature_level * LOCK_DIFFICULTY_BASE + random.randint(-10, 20)
    trap_state = {}
    if server and getattr(server, "traps", None):
        trap_state = server.traps.build_box_trap_state(creature_level) or {}
    else:
        trap_type = _random_trap(creature_level, server=None)
        trap_per_level = 4
        trap_jitter_low = -8
        trap_jitter_high = 10
        trap_state = {
            "trap_type": trap_type,
            "trapped": trap_type is not None,
            "trap_difficulty": (creature_level * trap_per_level + random.randint(trap_jitter_low, trap_jitter_high)) if trap_type else 0,
            "trap_checked": False,
            "trap_detected": False,
            "trap_disarmed": False,
            "trap_variant": None,
            "trap_payload": {},
        }

    box = None

    try:
        if db:
            query = """
                SELECT id, name, short_name, noun, article, container_capacity, description, container_type, base_name
                FROM items
                WHERE item_type = 'container'
                  AND is_template = 1
                  AND base_name = %s
                LIMIT 1
            """
            result = db.execute_query(query, (chosen_name,))
            if result and len(result) > 0:
                row = result[0]
                box = {
                    "item_id":            row[0],
                    "name":               row[1],
                    "short_name":         row[2],
                    "noun":               row[3],
                    "article":            row[4] or "a",
                    "container_capacity": row[5],
                    "description":        row[6],
                    "item_type":          "container",
                    "container_type":     row[7] or "treasure",
                    "base_name":          row[8] or chosen_name,
                }
    except Exception as e:
        log.warning(f"Failed to query box template: {e}")

    # Fallback if DB unavailable or no result
    if not box:
        short = chosen_name
        box = {
            "name":               "a " + chosen_name,
            "short_name":         chosen_name,
            "noun":               chosen_name.split()[-1],
            "article":            "a",
            "container_capacity": 5,
            "description":        "A sturdy " + chosen_name + ".",
            "item_type":          "container",
            "container_type":     "treasure",
            "base_name":          chosen_name,
        }

    box.update({
        "creature_level":   int(creature_level or 1),
        "lock_difficulty":  max(10, lock_diff),
        "is_locked":        True,
        "opened":           False,
        "trap_type":        trap_state.get("trap_type"),
        "trapped":          bool(trap_state.get("trapped")),
        "trap_difficulty":  int(trap_state.get("trap_difficulty", 0) or 0),
        "trap_checked":     bool(trap_state.get("trap_checked", False)),
        "trap_detected":    bool(trap_state.get("trap_detected", False)),
        "trap_disarmed":    bool(trap_state.get("trap_disarmed", False)),
        "trap_variant":     trap_state.get("trap_variant"),
        "trap_payload":     dict(trap_state.get("trap_payload") or {}),
        "contents":         [],   # populated below
    })

    # Generate contents now so they travel with the box
    box["contents"] = generate_box_contents(db, creature_level)

    return box


def generate_scroll(db, creature_level):
    """Pick a random scroll from the DB. Returns item dict or None."""
    try:
        query = """
            SELECT id, name, short_name, noun, value, description
            FROM items
            WHERE item_type = 'scroll'
              AND is_template = 1
            ORDER BY RAND()
            LIMIT 1
        """
        result = db.execute_query(query)
        if result and len(result) > 0:
            row = result[0]
            return {
                "item_id": row[0],
                "name": row[1],
                "short_name": row[2],
                "noun": row[3],
                "value": row[4],
                "description": row[5],
                "item_type": "scroll",
            }
    except Exception as e:
        log.warning(f"Failed to query scroll template: {e}")

    return None


def generate_wand(db, creature_level):
    """Pick a spell-backed wand profile appropriate to the creature level."""
    try:
        max_cost = max(8, min(25, int(creature_level or 1) + 8))
        query = """
            SELECT spell_number, name, spell_type, mana_cost
            FROM spells
            WHERE spell_type IN ('bolt', 'warding', 'utility', 'buff')
              AND mana_cost <= %s
            ORDER BY RAND()
            LIMIT 1
        """
        result = db.execute_query(query, (max_cost,))
        if result and len(result) > 0:
            row = result[0]
            name = random.choice(_FALLBACK_WANDS)
            return {
                "name":         name,
                "short_name":   name.lstrip("a ").lstrip("an "),
                "noun":         "wand",
                "item_type":    "wand",
                "value":        max(40, int(creature_level or 1) * 40),
                "charges":      random.randint(1, 5),
                "spell_number": int(row[0] or 0),
                "spell_name":   row[1],
                "spell_type":   row[2],
                "spell_level":  int(row[3] or 1),
            }
    except Exception as e:
        log.warning(f"Failed to query wand spell profile: {e}")

    return None


def generate_herb(db, creature_level):
    """Pick a random herb from the DB appropriate for level. Returns item dict or None."""
    try:
        # Pick herbs with value scaled to creature level
        max_val = creature_level * 50 + 100
        query = """
            SELECT id, name, short_name, noun, article, value, description,
                   heal_type, heal_amount, heal_rank
            FROM items
            WHERE item_type = 'herb'
              AND is_template = 1
              AND value <= %s
            ORDER BY RAND()
            LIMIT 1
        """
        result = db.execute_query(query, (max_val,))
        if result and len(result) > 0:
            row = result[0]
            return {
                "item_id":      row[0],
                "name":         row[1],
                "short_name":   row[2],
                "noun":         row[3],
                "article":      row[4],
                "value":        row[5],
                "description":  row[6],
                "item_type":    "herb",
                "heal_type":    row[7],
                "heal_amount":  row[8],
                "heal_rank":    row[9],
            }
    except Exception as e:
        log.warning(f"Failed to query herb template: {e}")

    return None


def _random_trap(creature_level, server=None):
    """Possibly generate a trap type for a box based on creature level.
    Uses weighted random selection from TRAP_WEIGHTS tiers."""
    if server and getattr(server, "traps", None):
        return server.traps.choose_random_trap(creature_level)
    if creature_level < 3:
        return None
    trap_chance = min(0.6, creature_level * 0.03)
    if random.random() > trap_chance:
        return None

    # Find the right weight tier for this level
    weights = None
    for (lo, hi), w in TRAP_WEIGHTS.items():
        if lo <= creature_level <= hi:
            weights = w
            break
    if not weights:
        weights = list(TRAP_WEIGHTS.values())[-1]

    # Weighted random choice
    trap_types = list(weights.keys())
    trap_wts   = list(weights.values())
    total = sum(trap_wts)
    roll  = random.random() * total
    cumul = 0
    for tt, tw in zip(trap_types, trap_wts):
        cumul += tw
        if roll <= cumul:
            return tt
    return trap_types[-1]



# ── GS4 Trap Definitions ── All 16 real trap types ────────────────────────────
# Each trap defines:
#   examine      — text shown on DETECT when trap is revealed
#   disarm_msg   — success message
#   fail_msg     — message when trap fires on player
#   room_msg     — broadcast to room on trap fire ({name} = character name)
#   dmg_min/max  — damage range when fired
#   damage_type  — puncture, crush, poison, slash, magic, fire, impact
#   effect       — secondary effect text (or None)
#   diff_bonus   — added to base trap difficulty
#   tools        — list of tool nouns required to disarm (order matters for multi-tool)
#   tool_action  — flavor text describing tool usage per step
#
# Tool nouns match item.noun in DB:
#   putty, cotton, vials (acid), grips, file, needle, lockpick (for sphere trap)
#   "dagger" = any weapon with noun "dagger" (scarab/scales alternate)
#   "scrape" = no tool needed, just scrape (glyph)
#   "force"  = brute force, no tool (springs)

TRAP_DEFS = {
    "scarab": {
        "examine":     "You notice a small scarab-like mechanism wedged between the lid and the rim.",
        "disarm_msg":  "You press putty over the scarab mechanism, gumming it into stillness, then carefully pry it free.",
        "fail_msg":    "A mechanical scarab bursts from the box and latches onto your hand, biting repeatedly!",
        "room_msg":    "{name} recoils as a bronze scarab flies out and attacks!",
        "dmg_min": 20, "dmg_max": 40,
        "damage_type": "slash",
        "effect":      None,
        "diff_bonus":  15,
        "tools":       ["putty"],
        "tool_action": ["You press putty firmly over the scarab mechanism, gumming its legs in place."],
    },
    "needle": {
        "examine":     "You notice a thin poison needle poised to spring from just under the lid.",
        "disarm_msg":  "You pack putty around the needle shaft, preventing it from firing, and bend it safely aside.",
        "fail_msg":    "A needle shoots out, pricking your finger! You feel a burning sensation spread through your hand.",
        "room_msg":    "{name} yelps and pulls back a pricked hand!",
        "dmg_min": 5,  "dmg_max": 15,
        "damage_type": "puncture",
        "effect":      "A numbing poison courses through your veins.",
        "diff_bonus":  0,
        "tools":       ["putty"],
        "tool_action": ["You carefully pack putty around the needle mechanism, immobilizing it."],
    },
    "jaws": {
        "examine":     "You notice a set of steel jaws mechanism designed to snap shut when the lid is opened.",
        "disarm_msg":  "You wedge the grips into the jaw mechanism, holding it open, and bend the trigger spring flat.",
        "fail_msg":    "Steel jaws snap shut on your fingers!",
        "room_msg":    "{name} cries out as steel jaws snap shut on their hand!",
        "dmg_min": 15, "dmg_max": 30,
        "damage_type": "crush",
        "effect":      None,
        "diff_bonus":  5,
        "tools":       ["grips"],
        "tool_action": ["You wedge the metal grips into the jaw mechanism, forcing it to stay open."],
    },
    "sphere": {
        "examine":     "You notice a small crystal sphere balanced precariously inside the lock mechanism.",
        "disarm_msg":  "You carefully guide the sphere out through the keyhole with your lockpick and set it aside.",
        "fail_msg":    "The crystal sphere shatters, releasing a burst of energy!",
        "room_msg":    "A bright flash erupts from {name}'s box as something shatters inside!",
        "dmg_min": 15, "dmg_max": 35,
        "damage_type": "magic",
        "effect":      "The energy discharge makes your hands tingle painfully.",
        "diff_bonus":  10,
        "tools":       ["lockpick"],
        "tool_action": ["You carefully guide the sphere out through the keyhole using the tip of your lockpick."],
    },
    "dark_crystal": {
        "examine":     "You notice a dark crystal shard wedged into the locking mechanism, pulsing faintly.",
        "disarm_msg":  "You file down the crystal shard until it crumbles into harmless dust.",
        "fail_msg":    "The dark crystal flares with energy, sending a jolt of pain through your body!",
        "room_msg":    "A dark pulse of energy erupts from {name}'s box!",
        "dmg_min": 20, "dmg_max": 45,
        "damage_type": "magic",
        "effect":      "You feel your mana reserves drained.",
        "diff_bonus":  15,
        "tools":       ["file"],
        "tool_action": ["You carefully file down the dark crystal shard until it crumbles to harmless powder."],
    },
    "scales": {
        "examine":     "You notice the lock mechanism is coated in some kind of metallic scale-like plating.",
        "disarm_msg":  "You pick the lock first, then carefully scrape the scales away with your dagger.",
        "fail_msg":    "The metallic scales explode outward, slicing your hands!",
        "room_msg":    "{name} flinches as metallic shrapnel sprays from the box!",
        "dmg_min": 18, "dmg_max": 38,
        "damage_type": "slash",
        "effect":      None,
        "diff_bonus":  10,
        "tools":       ["lockpick"],
        "tool_action": ["You use your lockpick to carefully work around the scale plating in the lock."],
    },
    "sulphur": {
        "examine":     "You detect a faint sulphurous odor emanating from a compound packed around the lock mechanism.",
        "disarm_msg":  "You file away the sulphur compound, then use the needle to release the trigger catch.",
        "fail_msg":    "The sulphur compound ignites! A flash of fire singes your hands and face!",
        "room_msg":    "A flash of fire erupts from {name}'s box with a sulphurous stench!",
        "dmg_min": 22, "dmg_max": 48,
        "damage_type": "fire",
        "effect":      "Your hands are badly singed.",
        "diff_bonus":  15,
        "tools":       ["file", "needle"],
        "tool_action": [
            "You carefully file away the sulphur compound packed around the mechanism.",
            "You probe with the needle to release the trigger catch beneath.",
        ],
    },
    "gas": {
        "examine":     "You spot a tiny vial of compressed gas wired to the lock mechanism.",
        "disarm_msg":  "You grip the vial firmly with the metal grips and carefully disconnect the trigger wire.",
        "fail_msg":    "A cloud of noxious gas billows out into your face!",
        "room_msg":    "A cloud of green gas erupts from {name}'s box!",
        "dmg_min": 15, "dmg_max": 35,
        "damage_type": "poison",
        "effect":      "You feel nauseated and weak.",
        "diff_bonus":  10,
        "tools":       ["grips"],
        "tool_action": ["You grip the gas vial firmly with the metal grips and disconnect the trigger wire."],
    },
    "acid": {
        "examine":     "You notice a thin glass vial of corrosive acid balanced above the lock, ready to tip.",
        "disarm_msg":  "You soak the cotton around the vial to catch any drips, then grip it steady and remove it.",
        "fail_msg":    "The acid vial tips and shatters! Corrosive liquid splashes across your hands!",
        "room_msg":    "{name} hisses in pain as acid splashes from the box!",
        "dmg_min": 18, "dmg_max": 42,
        "damage_type": "poison",
        "effect":      "The acid burns into your skin.",
        "diff_bonus":  12,
        "tools":       ["cotton", "grips"],
        "tool_action": [
            "You pack cotton balls around the acid vial to absorb any spillage.",
            "You grip the vial with the metal grips and carefully lift it free.",
        ],
    },
    "spring": {
        "examine":     "You spot a coiled spring mechanism that will snap the lid shut violently.",
        "disarm_msg":  "You wedge the grips against the spring coil and bend it until it loses tension.",
        "fail_msg":    "The lid snaps shut on your fingers!",
        "room_msg":    "{name} gets their fingers snapped by the box lid!",
        "dmg_min": 8,  "dmg_max": 20,
        "damage_type": "crush",
        "effect":      None,
        "diff_bonus":  5,
        "tools":       ["grips"],
        "tool_action": ["You wedge the metal grips against the spring coil and bend it flat."],
    },
    "fire_vial": {
        "examine":     "You notice a vial of volatile liquid wired into the lock — it will ignite if disturbed.",
        "disarm_msg":  "You carefully grip the vial and disconnect the trigger wire before it can shatter.",
        "fail_msg":    "The vial shatters and its contents ignite in a burst of flame!",
        "room_msg":    "Flames erupt from {name}'s box!",
        "dmg_min": 25, "dmg_max": 50,
        "damage_type": "fire",
        "effect":      "Your hands and sleeves catch fire briefly.",
        "diff_bonus":  18,
        "tools":       ["grips"],
        "tool_action": ["You carefully grip the fire vial with the metal grips and disconnect the trigger wire."],
    },
    "spores": {
        "examine":     "You detect a sealed compartment packed with toxic spores, designed to burst open on the lid.",
        "disarm_msg":  "You press putty over the spore compartment seal, preventing it from rupturing.",
        "fail_msg":    "Toxic spores explode from the box, engulfing you in a choking cloud!",
        "room_msg":    "A cloud of dark spores erupts from {name}'s box!",
        "dmg_min": 20, "dmg_max": 40,
        "damage_type": "poison",
        "effect":      "You cough and wheeze as the spores fill your lungs.",
        "diff_bonus":  12,
        "tools":       ["putty"],
        "tool_action": ["You press putty firmly over the spore compartment, sealing it shut."],
    },
    "plate": {
        "examine":     "You notice a thin metal plate wired across the lock — it will trigger if the wrong key is used.",
        "disarm_msg":  "You drip acid on the plate's anchor points, dissolving them, and the plate falls away harmlessly.",
        "fail_msg":    "The metal plate triggers, releasing a burst of shrapnel!",
        "room_msg":    "Shrapnel sprays from {name}'s box!",
        "dmg_min": 22, "dmg_max": 45,
        "damage_type": "slash",
        "effect":      None,
        "diff_bonus":  14,
        "tools":       ["vials"],
        "tool_action": ["You carefully drip acid from the vial onto the plate's anchor points, dissolving them."],
    },
    "glyph": {
        "examine":     "You see a faintly glowing glyph inscribed on the inner lid — a magical ward.",
        "disarm_msg":  "You carefully scrape away the glyph markings, disrupting the magical ward.",
        "fail_msg":    "The glyph flares and a bolt of energy strikes you!",
        "room_msg":    "A blinding flash erupts from {name}'s box!",
        "dmg_min": 25, "dmg_max": 55,
        "damage_type": "magic",
        "effect":      "You feel your mana reserves drained.",
        "diff_bonus":  20,
        "tools":       [],
        "tool_action": [],
    },
    "rods": {
        "examine":     "You notice thin metal rods poised to spring outward when the lock is tampered with.",
        "disarm_msg":  "You grip the rods with the metal grips and bend them safely aside.",
        "fail_msg":    "Metal rods spring out, stabbing into your hands!",
        "room_msg":    "{name} recoils as metal rods spring from the box!",
        "dmg_min": 18, "dmg_max": 38,
        "damage_type": "puncture",
        "effect":      None,
        "diff_bonus":  10,
        "tools":       ["grips"],
        "tool_action": ["You grip the metal rods firmly and bend them safely to the side."],
    },
    "boomer": {
        "examine":     "You spot a packed charge of volatile powder — this trap will explode.",
        "disarm_msg":  "You carefully press putty over the ignition point and extract the powder charge.",
        "fail_msg":    "The box EXPLODES in your hands!",
        "room_msg":    "{name}'s box EXPLODES with a deafening crack!",
        "dmg_min": 40, "dmg_max": 80,
        "damage_type": "fire",
        "effect":      "Your hands are badly burned.",
        "diff_bonus":  30,
        "tools":       ["putty"],
        "tool_action": ["You press putty over the ignition point, smothering it, and carefully extract the charge."],
    },
}

# Trap spawn weights by level range — higher-level creatures have nastier traps
TRAP_WEIGHTS = {
    # (min_level, max_level): {trap_type: weight}
    (1, 5): {
        "needle": 30, "spring": 25, "jaws": 15, "scarab": 10,
        "sphere": 10, "scales": 5, "gas": 5,
    },
    (6, 10): {
        "needle": 15, "spring": 15, "jaws": 15, "scarab": 12,
        "sphere": 10, "scales": 8, "gas": 8, "spores": 5,
        "rods": 5, "acid": 4, "plate": 3,
    },
    (11, 15): {
        "needle": 8, "spring": 8, "jaws": 10, "scarab": 10,
        "sphere": 8, "scales": 8, "gas": 8, "spores": 6,
        "rods": 6, "acid": 6, "plate": 5, "dark_crystal": 5,
        "sulphur": 4, "fire_vial": 4, "glyph": 2, "boomer": 2,
    },
    (16, 20): {
        "jaws": 6, "scarab": 8, "gas": 6, "spores": 6,
        "rods": 6, "acid": 8, "plate": 8, "dark_crystal": 8,
        "sulphur": 8, "fire_vial": 8, "glyph": 8, "boomer": 6,
        "needle": 4, "spring": 4, "sphere": 4, "scales": 2,
    },
    (21, 99): {
        "acid": 8, "plate": 8, "dark_crystal": 10, "sulphur": 10,
        "fire_vial": 10, "glyph": 12, "boomer": 12,
        "scarab": 6, "gas": 6, "spores": 6, "rods": 6,
        "jaws": 2, "needle": 2, "spring": 0, "sphere": 2, "scales": 0,
    },
}




# -- Box contents generation ------------------------------------------------

# Items that can appear inside boxes, tiered by creature level
BOX_CONTENT_TABLES = {
    # (level_min, level_max): list of (weight, category, value_min, value_max)
    # categories: coins, gem, scroll, herb, weapon, armor, wand
    (1,  5):  [(30, "gem",    10,  150),
               (25, "scroll", 0,   0),
               (25, "herb",   0,   0),
               (20, "wand",   0,   0)],
    (6,  10): [(30, "gem",    50,  400),
               (25, "scroll", 0,   0),
               (25, "herb",   0,   0),
               (20, "wand",   0,   0)],
    (11, 15): [(30, "gem",    100, 800),
               (25, "scroll", 0,   0),
               (25, "herb",   0,   0),
               (20, "wand",   0,   0)],
    (16, 99): [(30, "gem",    200, 1500),
               (25, "scroll", 0,   0),
               (25, "herb",   0,   0),
               (20, "wand",   0,   0)],
}

# Fallback gem names by tier (used when DB unavailable)
_FALLBACK_GEMS = {
    (1,  5):  [("a grey pearl",       50), ("a polished agate",    35), ("a rose quartz",     25)],
    (6,  10): [("a small ruby",       90), ("a clear topaz",       75), ("a piece of jade",   60)],
    (11, 15): [("a blue sapphire",   160), ("a tiny emerald",     130), ("a pale aquamarine", 110)],
    (16, 99): [("a bright diamond",  350), ("a deep amethyst",    280), ("a blood red garnet",220)],
}

_FALLBACK_SCROLLS = [
    "a simple parchment scroll", "a tattered scroll", "a vellum scroll",
    "a singed scroll", "a water-stained scroll",
]

_FALLBACK_HERBS = [
    "some aloeas stems", "some ambrominas leaf", "some basal moss",
    "a clump of bur-clover", "some calamia fruit",
]

_FALLBACK_WANDS = [
    "a gnarled wand", "a polished wand", "a short wand", "a slender wand",
]


def _weighted_choice(table):
    """Pick a category from a weighted table."""
    total = sum(w for w, *_ in table)
    r = random.randint(1, total)
    running = 0
    for w, *rest in table:
        running += w
        if r <= running:
            return rest
    return table[-1][1:]


def _tier_val(tiers, level):
    for (lo, hi), val in tiers.items():
        if lo <= level <= hi:
            return val
    return list(tiers.values())[-1]


# Silver ranges for box contents - GUARANTEED per box (matches retail GS4)
BOX_SILVER_TIERS = {
    (1,  5):  (300,  1200),
    (6,  10): (500,  2000),
    (11, 15): (800,  3500),
    (16, 20): (1200, 5000),
    (21, 99): (2000, 10000),
}

def generate_box_contents(db, creature_level):
    """
    Generate 1 -- ¢Ã¢â€šÂ¬Ã¢â‚¬Å“3 items to place inside a treasure box.
    Returns a list of item dicts.

    Each item has at minimum: name, short_name, noun, item_type, value.
    Items also get a 'container_id' key which the caller must fill in
    with the box's inv_id once the box is placed in inventory.
    """
    table = _tier_val(BOX_CONTENT_TABLES, creature_level)

    # Number of NON-SILVER items: 2 guaranteed, up to 2 more
    num_items = 2
    if random.random() < 0.50:
        num_items += 1
    if random.random() < 0.20:
        num_items += 1

    contents = []

    # -€-€- GUARANTEED silver coins -€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-€-
    silver_min, silver_max = _get_tier_value(BOX_SILVER_TIERS, creature_level)
    silver_amount = random.randint(silver_min, silver_max)
    # Occasional jackpot (5% chance for 2x-4x silver)
    if random.random() < 0.05:
        silver_amount = int(silver_amount * random.uniform(2.0, 4.0))
    contents.append({
        "name":        f"{silver_amount} silver coins",
        "short_name":  "silver coins",
        "noun":        "coins",
        "item_type":   "coins",
        "value":       silver_amount,
        "coin_amount": silver_amount,
        "container_id": None,
    })

    # -€-€- Additional items (min 2, coins removed from loot table) -€-€-€-€-€-€-€-€-€-€-€-€-
    for _ in range(num_items):
        result = _weighted_choice(table)
        category = result[0]
        val_min  = result[1] if len(result) > 1 else 0
        val_max  = result[2] if len(result) > 2 else 0

        item = None

        if category == "coins":
            # Coins removed from table, but if we somehow land here,
            # treat as a bonus gem roll instead
            item = generate_gem(db, creature_level) if db else None

        elif category == "gem":
            if db:
                item = generate_gem(db, creature_level)
            if not item:
                gems = _tier_val(
                    {k: v for k, v in zip(_FALLBACK_GEMS.keys(), _FALLBACK_GEMS.values())},
                    creature_level
                )
                name, value = random.choice(gems)
                short = name.lstrip("a ").lstrip("an ").lstrip("some ")
                item = {
                    "name":       name,
                    "short_name": short,
                    "noun":       short.split()[-1],
                    "item_type":  "gem",
                    "value":      value,
                }

        elif category == "scroll":
            if db:
                item = generate_scroll(db, creature_level)
            if not item:
                name = random.choice(_FALLBACK_SCROLLS)
                item = {
                    "name":       name,
                    "short_name": name.lstrip("a ").lstrip("an "),
                    "noun":       "scroll",
                    "item_type":  "scroll",
                    "value":      creature_level * 20,
                }

        elif category == "herb":
            if db:
                item = generate_herb(db, creature_level)
            if not item:
                name = random.choice(_FALLBACK_HERBS)
                item = {
                    "name":       name,
                    "short_name": name.lstrip("a ").lstrip("an ").lstrip("some "),
                    "noun":       name.split()[-1],
                    "item_type":  "herb",
                    "value":      creature_level * 15,
                }

        elif category == "wand":
            if db:
                item = generate_wand(db, creature_level)
            if not item:
                name = random.choice(_FALLBACK_WANDS)
                item = {
                    "name":       name,
                    "short_name": name.lstrip("a ").lstrip("an "),
                    "noun":       "wand",
                    "item_type":  "wand",
                    "value":      creature_level * 40,
                    "charges":    random.randint(1, 5),
                }

        if item:
            item["container_id"] = None  # caller fills this in
            contents.append(item)

    return contents


def generate_treasure(db, creature, server=None):
    """
    Generate all treasure drops for a killed creature.

    Args:
        db: Database connection with execute_query method
        creature: The dead creature instance

    Returns:
        dict with keys: coins (int), items (list of item dicts)
    """
    treasure_flags = creature.treasure
    level = creature.level
    result = {"coins": 0, "items": []}

    # Coins
    if treasure_flags.get("coins"):
        result["coins"] = generate_coins(level)

    # Gems (40% chance if flagged)
    if treasure_flags.get("gems") and random.random() < 0.4:
        gem = generate_gem(db, level)
        if gem:
            result["items"].append(gem)
        # Second gem at higher levels (20% chance)
        if level >= 10 and random.random() < 0.2:
            gem2 = generate_gem(db, level)
            if gem2:
                result["items"].append(gem2)

    # Boxes (30% chance if flagged)
    if treasure_flags.get("boxes") and random.random() < 0.3:
        box = generate_box(db, level, server=server)
        if box:
            result["items"].append(box)

    # Magic items (scrolls, wands - 15% chance if flagged)
    if treasure_flags.get("magic") and random.random() < 0.15:
        scroll = generate_scroll(db, level)
        if scroll:
            result["items"].append(scroll)

    # Herbs (10% chance on any creature with gems flag)
    if treasure_flags.get("gems") and random.random() < 0.1:
        herb = generate_herb(db, level)
        if herb:
            result["items"].append(herb)

    # Some creatures carry special drops through authored abilities rather than
    # explicit special_loot tables. Fold those in before building the corpse.
    for ability_id, item_name in ABILITY_SPECIAL_LOOT.items():
        if ability_id in {str(a or "").lower() for a in (getattr(creature, "abilities", []) or [])}:
            if item_name not in (getattr(creature, "special_loot", []) or []):
                creature.special_loot.append(item_name)

    # Authored creature-specific loot should surface on corpses independently
    # of the generic treasure flag lane.
    for special_name in list(getattr(creature, "special_loot", []) or []):
        if not isinstance(special_name, str):
            continue
        short_name = special_name.strip()
        if not short_name or random.random() > 0.45:
            continue
        words = short_name.split()
        first_word = words[0].lower() if words else ""
        article = first_word if first_word in {"a", "an", "the", "some"} else "a"
        noun = words[-1].lower() if words else "item"
        item_id = None
        if db:
            item_id = db.get_or_create_item(
                name=short_name,
                short_name=short_name,
                noun=noun,
                item_type="misc",
                article=article,
                value=max(5, int(level or 1) * 20),
                description=f"{short_name.capitalize()} recovered from {getattr(creature, 'full_name', getattr(creature, 'name', 'a creature'))}.",
            )
        result["items"].append({
            "item_id": item_id,
            "name": short_name,
            "short_name": short_name,
            "noun": noun,
            "item_type": "misc",
            "value": max(5, int(level or 1) * 20),
            "description": f"{short_name.capitalize()} recovered from {getattr(creature, 'full_name', getattr(creature, 'name', 'a creature'))}.",
        })

    # If a creature stole real inventory from someone, that property should
    # return when the creature is looted.
    for stolen in list(getattr(creature, "stolen_items", []) or []):
        if isinstance(stolen, dict):
            result["items"].append(dict(stolen))

    return result
