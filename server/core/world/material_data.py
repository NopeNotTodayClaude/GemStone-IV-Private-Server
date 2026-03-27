"""
material_data.py  –  GemStone IV canonical materials.

Each entry defines:
  name          str    canonical name (lowercase, used as key)
  display       str    pretty-print name
  rarity        str    common / uncommon / rare / very_rare / extremely_rare
  level_req     int    minimum character level to use this item
  enchant_bonus int    base enchantment bonus (+0 to +50)
  attack_mod    int    attack-strength modifier for weapons
  defense_mod   int    defense-strength modifier for armor/shields
  cost_mult     float  price multiplier over base item cost
  apply_to      list   which item types this material applies to
  description   str    flavor text shown in CUSTOMIZE list
  special       str    special property (cold_flare, fire_flare, etc.) - optional
  weight_modifier float modifier on item weight (1.0 = normal) - optional

Enchant bonus → level requirement formula (GS4 canon):
  level_req = ceil(enchant_bonus / 2)

Applies-to codes:
  "weapon"  "armor"  "shield"  "jewelry"  "all"
"""

from math import ceil

MATERIALS = {
    # ── Common / starter metals ───────────────────────────────────────────────
    "iron": {
        "display": "iron",
        "rarity": "common",
        "level_req": 0,
        "enchant_bonus": 0,
        "attack_mod": 0,
        "defense_mod": 0,
        "cost_mult": 1.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "Ordinary iron.  No enchantment bonus.",
        "weight_modifier": 1.0,
    },
    "steel": {
        "display": "steel",
        "rarity": "common",
        "level_req": 0,
        "enchant_bonus": 0,
        "attack_mod": 0,
        "defense_mod": 0,
        "cost_mult": 1.2,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "Quality steel.  Reliable and well-balanced.",
        "weight_modifier": 1.0,
    },
    "bronze": {
        "display": "bronze",
        "rarity": "common",
        "level_req": 0,
        "enchant_bonus": 0,
        "attack_mod": 0,
        "defense_mod": 0,
        "cost_mult": 1.0,
        "apply_to": ["weapon", "armor", "shield", "jewelry"],
        "description": "Common bronze alloy.",
        "weight_modifier": 1.0,
    },
    "silver": {
        "display": "silver",
        "rarity": "uncommon",
        "level_req": 0,
        "enchant_bonus": 0,
        "attack_mod": 0,
        "defense_mod": 0,
        "cost_mult": 2.0,
        "apply_to": ["weapon", "jewelry"],
        "description": "Pure silver.  Effective against certain undead.",
        "weight_modifier": 0.95,
    },
    "gold": {
        "display": "gold",
        "rarity": "uncommon",
        "level_req": 0,
        "enchant_bonus": 0,
        "attack_mod": 0,
        "defense_mod": 0,
        "cost_mult": 3.0,
        "apply_to": ["jewelry"],
        "description": "Lustrous gold, popular for jewelry.",
        "weight_modifier": 0.95,
    },
    "invar": {
        "display": "invar",
        "rarity": "infrequent",
        "level_req": 1,
        "enchant_bonus": 2,
        "attack_mod": 2,
        "defense_mod": 2,
        "cost_mult": 1.5,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A dull grey metal with a slight enchantment.",
        "weight_modifier": 0.95,
    },

    # ── Uncommon metals ───────────────────────────────────────────────────────
    "mithril": {
        "display": "mithril",
        "rarity": "uncommon",
        "level_req": 3,
        "enchant_bonus": 5,
        "attack_mod": 5,
        "defense_mod": 5,
        "cost_mult": 4.0,
        "apply_to": ["weapon", "armor", "shield", "jewelry"],
        "description": "A silvery metal of moderate enchantment.  Requires level 3.",
        "weight_modifier": 0.75,
    },
    "ora": {
        "display": "ora",
        "rarity": "uncommon",
        "level_req": 5,
        "enchant_bonus": 10,
        "attack_mod": 10,
        "defense_mod": 10,
        "cost_mult": 6.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A warm golden-hued metal.  Requires level 5.",
        "weight_modifier": 0.9,
    },
    "imflass": {
        "display": "imflass",
        "rarity": "uncommon",
        "level_req": 6,
        "enchant_bonus": 12,
        "attack_mod": 12,
        "defense_mod": 12,
        "cost_mult": 7.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A bluish-grey metal of good enchantment.  Requires level 6.",
        "weight_modifier": 0.85,
    },
    "laje": {
        "display": "laje",
        "rarity": "infrequent",
        "level_req": 6,
        "enchant_bonus": 10,
        "attack_mod": 10,
        "defense_mod": 10,
        "cost_mult": 5.0,
        "apply_to": ["weapon", "jewelry"],
        "description": "A dark, dense metal with minor magical properties.",
        "weight_modifier": 0.85,
    },
    "carmiln": {
        "display": "carmiln",
        "rarity": "uncommon",
        "level_req": 4,
        "enchant_bonus": 8,
        "attack_mod": 8,
        "defense_mod": 8,
        "cost_mult": 4.5,
        "apply_to": ["weapon", "armor", "shield", "jewelry"],
        "description": "A reddish metal with moderate magical resonance.",
        "weight_modifier": 0.9,
    },

    # ── Rare metals ───────────────────────────────────────────────────────────
    "faenor": {
        "display": "faenor",
        "rarity": "rare",
        "level_req": 4,
        "enchant_bonus": 8,
        "attack_mod": 8,
        "defense_mod": 8,
        "cost_mult": 8.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A pale silver metal with solid enchantment.  Requires level 4.",
        "weight_modifier": 0.7,
    },
    "gornar": {
        "display": "gornar",
        "rarity": "rare",
        "level_req": 3,
        "enchant_bonus": 5,
        "attack_mod": 5,
        "defense_mod": 5,
        "cost_mult": 5.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A dark, heavy metal known for durability.",
        "weight_modifier": 1.1,
    },
    "rhimar": {
        "display": "rhimar",
        "rarity": "rare",
        "level_req": 3,
        "enchant_bonus": 5,
        "attack_mod": 5,
        "defense_mod": 5,
        "cost_mult": 5.5,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A blue-tinged ice-cold metal.  Causes cold flares.",
        "special": "cold_flare",
        "weight_modifier": 0.9,
    },
    "zorchar": {
        "display": "zorchar",
        "rarity": "rare",
        "level_req": 3,
        "enchant_bonus": 5,
        "attack_mod": 5,
        "defense_mod": 5,
        "cost_mult": 5.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A red-orange metal with fire resonance.",
        "special": "lightning_flare",
        "weight_modifier": 0.9,
    },
    "drakar": {
        "display": "drakar",
        "rarity": "rare",
        "level_req": 3,
        "enchant_bonus": 5,
        "attack_mod": 5,
        "defense_mod": 5,
        "cost_mult": 5.0,
        "apply_to": ["weapon"],
        "description": "A dark metal prized by warriors.",
        "special": "fire_flare",
        "weight_modifier": 0.9,
    },
    "razern": {
        "display": "razern",
        "rarity": "rare",
        "level_req": 5,
        "enchant_bonus": 10,
        "attack_mod": 10,
        "defense_mod": 10,
        "cost_mult": 9.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "An extremely sharp metal.  Razor-edged.",
        "special": "acid_flare",
        "weight_modifier": 0.95,
    },
    "vaalorn": {
        "display": "vaalorn",
        "rarity": "rare",
        "level_req": 9,
        "enchant_bonus": 18,
        "attack_mod": 18,
        "defense_mod": 18,
        "cost_mult": 14.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A silvery-blue elvish metal of strong enchantment.  Requires level 9.",
        "weight_modifier": 0.8,
    },

    # ── Very rare metals ──────────────────────────────────────────────────────
    "glaes": {
        "display": "glaes",
        "rarity": "uncommon",
        "level_req": 8,
        "enchant_bonus": 15,
        "attack_mod": 15,
        "defense_mod": 15,
        "cost_mult": 10.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A black glassy volcanic metal.  Requires level 8.",
        "weight_modifier": 0.85,
    },
    "mithglin": {
        "display": "mithglin",
        "rarity": "rare",
        "level_req": 8,
        "enchant_bonus": 15,
        "attack_mod": 15,
        "defense_mod": 15,
        "cost_mult": 11.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A dark, heavy dwarven metal.  Requires level 8.",
        "weight_modifier": 0.95,
    },
    "eahnor": {
        "display": "eahnor",
        "rarity": "very_rare",
        "level_req": 9,
        "enchant_bonus": 18,
        "attack_mod": 18,
        "defense_mod": 18,
        "cost_mult": 15.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A deep red elvish metal.  Requires level 9.",
        "special": "undead_bane",
        "weight_modifier": 0.8,
    },
    "vultite": {
        "display": "vultite",
        "rarity": "uncommon",
        "level_req": 10,
        "enchant_bonus": 20,
        "attack_mod": 20,
        "defense_mod": 20,
        "cost_mult": 16.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A bright green metal of high enchantment.  Requires level 10.",
        "weight_modifier": 0.8,
    },
    "rolaren": {
        "display": "rolaren",
        "rarity": "very_rare",
        "level_req": 10,
        "enchant_bonus": 20,
        "attack_mod": 20,
        "defense_mod": 20,
        "cost_mult": 18.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A bright silver metal of high enchantment.  Requires level 10.",
        "weight_modifier": 0.85,
    },
    "eonake": {
        "display": "eonake",
        "rarity": "very_rare",
        "level_req": 10,
        "enchant_bonus": 20,
        "attack_mod": 20,
        "defense_mod": 20,
        "cost_mult": 18.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A shimmering goldish metal.  Requires level 10.",
        "special": "undead_bane",
        "weight_modifier": 0.8,
    },
    "kelyn": {
        "display": "kelyn",
        "rarity": "very_rare",
        "level_req": 10,
        "enchant_bonus": 20,
        "attack_mod": 20,
        "defense_mod": 20,
        "cost_mult": 17.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A dense dark metal found deep underground.",
        "weight_modifier": 0.9,
    },
    "urglaes": {
        "display": "urglaes",
        "rarity": "very_rare",
        "level_req": 10,
        "enchant_bonus": 20,
        "attack_mod": 20,
        "defense_mod": 20,
        "cost_mult": 20.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A black form of glaes with a dark energy.  Requires level 10.",
        "special": "anti_magic",
        "weight_modifier": 0.85,
    },

    # ── Extremely rare / endgame ───────────────────────────────────────────────
    "golvern": {
        "display": "golvern",
        "rarity": "very_rare",
        "level_req": 13,
        "enchant_bonus": 25,
        "attack_mod": 25,
        "defense_mod": 25,
        "cost_mult": 28.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A golden metal of exceptional power.  Requires level 13.",
        "weight_modifier": 0.85,
    },
    "krodera": {
        "display": "krodera",
        "rarity": "very_rare",
        "level_req": 13,
        "enchant_bonus": 25,
        "attack_mod": 25,
        "defense_mod": 25,
        "cost_mult": 30.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "An extremely hard dark metal.  Requires level 13.",
        "special": "anti_magic",
        "weight_modifier": 1.2,
    },
    "kroderine": {
        "display": "kroderine",
        "rarity": "very_rare",
        "level_req": 13,
        "enchant_bonus": 25,
        "attack_mod": 25,
        "defense_mod": 25,
        "cost_mult": 30.0,
        "apply_to": ["weapon", "armor", "shield"],
        "description": "A refined form of krodera with greater potency.",
        "special": "anti_magic",
        "weight_modifier": 1.15,
    },
    "veniom": {
        "display": "veniom",
        "rarity": "very_rare",
        "level_req": 10,
        "enchant_bonus": 20,
        "attack_mod": 15,
        "defense_mod": 20,
        "cost_mult": 22.0,
        "apply_to": ["armor", "shield", "jewelry"],
        "description": "An incredibly light metal — reduces encumbrance significantly.",
        "special": "featherweight",
        "weight_modifier": 0.5,
    },
    "coraesine": {
        "display": "coraesine",
        "rarity": "extremely_rare",
        "level_req": 20,
        "enchant_bonus": 35,
        "attack_mod": 35,
        "defense_mod": 30,
        "cost_mult": 80.0,
        "apply_to": ["weapon"],
        "description": "A legendary pale metal of immense destructive power.  Requires level 20.",
        "special": "disintegrate",
        "weight_modifier": 0.75,
    },
}

# ── Common colors (for ORDER # COLOR {name}) ──────────────────────────────────
COLORS = [
    "white", "grey", "black", "dark", "red", "blue", "azure", "cyan",
    "green", "yellow", "brown", "tan", "orange", "purple", "lavender",
    "golden", "silvery", "chrome", "brass", "crimson", "ebony", "ivory",
    "scarlet", "cobalt", "jade", "rose", "pink", "midnight", "shadow",
]

# ── Item type → which material apply_to values are valid ─────────────────────
# Fabric materials used for clothing (ASG 1-2 armor).
# Items made from these materials support color customization only —
# no enchantment, no attack/defense mods.
FABRIC_MATERIALS = {
    "linen", "wool", "cotton", "silk", "velvet",
    "satin", "brocade", "lace", "canvas", "hemp",
}


def is_clothing_item(item: dict) -> bool:
    """
    Returns True if this item is clothing (color-only customization).
    Clothing = armor with ASG 1-2 and a fabric material, OR any item
    whose material is a fabric (covers misc clothing items too).
    """
    mat   = (item.get("material") or "").lower().strip()
    itype = (item.get("item_type") or "").lower()
    asg   = int(item.get("armor_asg") or 0)

    if mat in FABRIC_MATERIALS:
        return True
    if itype == "armor" and asg <= 2:
        return True
    return False


def pretty_item_name(name: str) -> str:
    """
    Clean and capitalize an item's display name for player output.

    Strips ALL leading articles (a/an/the/some) before display.
    Reorders color before material when both are present.
    Never re-adds an article prefix.

    Examples:
      "a greatshield"               -> "Greatshield"
      "some flowing robes"          -> "Flowing robes"
      "a invar silvery scimitar"    -> "Silvery invar scimitar"
      "shadow glaes leather gloves" -> "Shadow glaes leather gloves"
      "some aloeas stems"           -> "Aloeas stems"
    """
    if not name:
        return name

    words = name.strip().split()
    if not words:
        return name

    # Strip ALL leading articles, loop until none remain
    _ARTICLES = {"a", "an", "the", "some", "some"}
    while words and words[0].lower() in _ARTICLES:
        words = words[1:]

    if not words:
        return name.capitalize()

    # Identify material and color words to reorder: color first, then material
    mat_display_set = {MATERIALS[m]["display"] for m in MATERIALS}
    color_set       = set(COLORS)

    found_mat   = None
    found_color = None
    other_words = []

    for w in words:
        wl = w.lower()
        if wl in mat_display_set and found_mat is None:
            found_mat = wl
        elif wl in color_set and found_color is None:
            found_color = wl
        else:
            other_words.append(w)

    # Rebuild: color  material  everything-else  (no article prefix ever)
    parts = []
    if found_color:
        parts.append(found_color)
    if found_mat:
        parts.append(found_mat)
    parts.extend(other_words)

    result = " ".join(parts)

    # Capitalize first letter only
    return result[0].upper() + result[1:] if result else result

ITEM_TYPE_COMPAT = {
    "weapon":  ["weapon", "all"],
    "armor":   ["armor", "all"],
    "shield":  ["shield", "armor", "all"],
    "jewelry": ["jewelry", "all"],
}


def get_material(name: str) -> dict | None:
    """Return material dict by name (case-insensitive), or None."""
    return MATERIALS.get(name.lower().strip())


def get_materials_for_item_type(item_type: str) -> list[dict]:
    """Return all materials valid for a given item type, sorted by level_req."""
    compat = ITEM_TYPE_COMPAT.get(item_type, [])
    result = [
        {"key": k, **v}
        for k, v in MATERIALS.items()
        if any(c in v["apply_to"] for c in compat)
    ]
    return sorted(result, key=lambda m: m["level_req"])


def can_use_material(player_level: int, material_name: str) -> tuple[bool, str]:
    """
    Returns (True, '') if the player meets the level requirement,
    or (False, reason_string) if not.
    """
    mat = get_material(material_name)
    if not mat:
        return False, f"'{material_name}' is not a recognized material."
    req = mat["level_req"]
    if player_level < req:
        return False, (
            f"You must be at least level {req} to wield {mat['display']} equipment.  "
            f"You are level {player_level}."
        )
    return True, ""


def apply_material_to_item(item: dict, material_name: str) -> dict:
    """
    Return a copy of item with material bonuses applied.
    Updates: name, short_name, enchant_bonus, attack_bonus, defense_bonus,
             level_required, value, material (new field).
    """
    mat = get_material(material_name)
    if not mat:
        return item

    import copy
    updated = copy.deepcopy(item)
    updated["material"] = mat["display"]

    # Replace the existing material word in both name fields in a single pass.
    # Strategy: find the first material whose display word appears in the name,
    # strip it from ALL name fields, then insert the new material word cleanly.
    # This avoids the double-replacement bug caused by the old for/else loop where
    # break only exited the inner field loop while the outer mat loop kept running.
    found_old = None
    for existing_mat in MATERIALS:
        old_display = MATERIALS[existing_mat]["display"]
        # Check name first, fall back to short_name
        if old_display in updated.get("name", "") or old_display in updated.get("short_name", ""):
            found_old = old_display
            break   # stop scanning — only replace the FIRST match

    if found_old:
        # Replace in both fields atomically
        for field in ("name", "short_name"):
            val = updated.get(field, "")
            if found_old in val:
                updated[field] = val.replace(found_old, mat["display"], 1)
            else:
                # Field didn't have the old material (e.g. short_name stored without prefix)
                # Prepend new material after the article if present, otherwise just prepend
                parts = val.split(" ", 1)
                if len(parts) == 2 and parts[0].lower() in ("a", "an", "the", "some"):
                    updated[field] = f"{parts[0]} {mat['display']} {parts[1]}"
                elif val:
                    updated[field] = f"{mat['display']} {val}"
    else:
        # No existing material found — prepend to both fields
        for field in ("name", "short_name"):
            val = updated.get(field, "")
            if val:
                parts = val.split(" ", 1)
                if len(parts) == 2 and parts[0].lower() in ("a", "an", "the", "some"):
                    updated[field] = f"{parts[0]} {mat['display']} {parts[1]}"
                else:
                    updated[field] = f"{mat['display']} {val}"

    # Fix article: "a invar" -> "an invar" and vice versa
    for field in ("name",):
        val = updated.get(field, "")
        words = val.split(" ", 2)
        if len(words) >= 2 and words[0].lower() in ("a", "an"):
            correct = "an" if words[1][0].lower() in "aeiou" else "a"
            if words[0].lower() != correct:
                updated[field] = correct + " " + " ".join(words[1:])

    # Apply stat bonuses
    item_type = updated.get("item_type", "misc")
    if item_type == "weapon":
        updated["attack_bonus"] = (updated.get("attack_bonus") or 0) + mat["attack_mod"]
        updated["enchant_bonus"] = mat["enchant_bonus"]
    elif item_type in ("armor", "shield"):
        updated["defense_bonus"] = (updated.get("defense_bonus") or 0) + mat["defense_mod"]
        updated["enchant_bonus"] = mat["enchant_bonus"]
    elif item_type == "jewelry":
        updated["enchant_bonus"] = mat["enchant_bonus"]

    # Level requirement
    updated["level_required"] = max(
        updated.get("level_required") or 0,
        mat["level_req"]
    )

    # Price multiplier
    base_value = updated.get("value") or 0
    updated["value"] = int(base_value * mat["cost_mult"])

    return updated


def apply_color_to_item(item: dict, color: str) -> dict:
    """
    Return a copy of item with the color inserted into its name.
    Color is inserted between the material word and the noun, so:
      'a invar falchion'  -> 'a invar silvery falchion'
      'a falchion'        -> 'a silvery falchion'
    """
    import copy
    color = color.lower().strip()
    if color not in COLORS:
        return item
    updated = copy.deepcopy(item)
    updated["color"] = color

    # Find which material is already in the item (if any)
    mat_display = updated.get("material", "")

    for field in ("name", "short_name"):
        val = updated.get(field, "")
        if not val or color in val:
            continue

        if mat_display and mat_display in val:
            # Insert color immediately after the material word
            # e.g. "a invar falchion" -> "a invar silvery falchion"
            idx = val.index(mat_display) + len(mat_display)
            updated[field] = val[:idx] + " " + color + val[idx:]
        else:
            # No material word — insert after article if present
            parts = val.split(" ", 1)
            if len(parts) == 2 and parts[0].lower() in ("a", "an", "the", "some"):
                updated[field] = f"{parts[0]} {color} {parts[1]}"
            else:
                updated[field] = f"{color} {val}"

    return updated
