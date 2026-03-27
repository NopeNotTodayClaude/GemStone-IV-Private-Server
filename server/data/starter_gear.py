"""
GemStone IV Starter Gear — Python Fallback
-------------------------------------------
This file is the LAST-RESORT fallback only.
The authoritative data lives in scripts/data/starter_gear.lua.

character_creation.py tries server.lua.get_starter_gear() first.
Only if the Lua engine is unavailable does it fall through here.

All 10 professions are defined so nobody is ever created naked.
Item IDs match the gemstone_items_seed.sql seeding order.
Containers MUST appear before any items placed inside them.
"""

# Starting silver per profession (prof_id -> amount)
STARTING_SILVER = {
    1:  5000,  # Warrior
    2:  5000,  # Rogue
    3:  5000,  # Wizard
    4:  5000,  # Cleric
    5:  5000,  # Empath
    6:  5000,  # Sorcerer
    7:  5000,  # Ranger
    8:  5000,  # Bard
    9:  5000,  # Paladin
    10: 5000,  # Monk
}

# slot: worn body slot  (back, belt, shoulders, torso, shoulder_slung, ...)
# hand: "right" or "left"  (placed directly in that hand)
# container: noun of container to place item inside ("backpack", "pouch", ...)
STARTER_GEAR = {
    1: {  # WARRIOR
        "description": "Warrior Starter Kit",
        "items": [
            {"item_id": 236, "name": "a leather backpack",           "slot": "back"},
            {"item_id": 238, "name": "a belt pouch",                 "slot": "belt"},
            {"item_id": 241, "name": "an adventurer's cloak",        "slot": "shoulders"},
            {"item_id": 75,  "name": "some reinforced leather armor","slot": "torso"},
            {"item_id": 94,  "name": "a steel target shield",        "slot": "shoulder_slung"},
            {"item_id": 9,   "name": "a steel longsword",            "hand": "right"},
            {"item_id": 2,   "name": "a steel dagger",               "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
        ],
    },
    2: {  # ROGUE
        "description": "Rogue Starter Kit",
        "items": [
            {"item_id": 236, "name": "a leather backpack",           "slot": "back"},
            {"item_id": 238, "name": "a belt pouch",                 "slot": "belt"},
            {"item_id": 241, "name": "an adventurer's cloak",        "slot": "shoulders"},
            {"item_id": 73,  "name": "some light leather armor",     "slot": "torso"},
            {"item_id": 93,  "name": "a steel buckler",              "slot": "shoulder_slung"},
            {"item_id": 7,   "name": "a steel short sword",          "hand": "right"},
            {"item_id": 2,   "name": "a steel dagger",               "container": "backpack"},
            {"item_id": 205, "name": "a crude lockpick",             "container": "pouch"},
            {"item_id": 205, "name": "a crude lockpick",             "container": "pouch"},
            {"item_id": 206, "name": "a simple lockpick",            "container": "pouch"},
            {"item_id": 206, "name": "a simple lockpick",            "container": "pouch"},
            {"item_id": 207, "name": "a standard lockpick",          "container": "pouch"},
        ],
    },
    3: {  # WIZARD
        "description": "Wizard Starter Kit",
        "items": [
            {"item_id": 236, "name": "a leather backpack",           "slot": "back"},
            {"item_id": 239, "name": "a herb pouch",                 "slot": "belt"},
            {"item_id": 242, "name": "a flowing silk cloak",         "slot": "shoulders"},
            {"item_id": 352, "name": "some flowing robes",           "slot": "torso"},
            {"item_id": 101, "name": "a wooden runestaff",           "hand": "right"},
            {"item_id": 750, "name": "a copper symbol",              "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
        ],
    },
    4: {  # CLERIC
        "description": "Cleric Starter Kit",
        "items": [
            {"item_id": 236, "name": "a leather backpack",           "slot": "back"},
            {"item_id": 238, "name": "a belt pouch",                 "slot": "belt"},
            {"item_id": 243, "name": "a white linen cloak",          "slot": "shoulders"},
            {"item_id": 76,  "name": "some double leather armor",    "slot": "torso"},
            {"item_id": 94,  "name": "a steel target shield",        "slot": "shoulder_slung"},
            {"item_id": 52,  "name": "a steel mace",                 "hand": "right"},
            {"item_id": 751, "name": "a holy symbol",                "container": "pouch"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 602, "name": "some wolifrew lichen",         "container": "backpack"},
            {"item_id": 603, "name": "some torban leaf",             "container": "backpack"},
        ],
    },
    5: {  # EMPATH
        "description": "Empath Starter Kit",
        "items": [
            {"item_id": 236, "name": "a leather backpack",           "slot": "back"},
            {"item_id": 239, "name": "a herb pouch",                 "slot": "belt"},
            {"item_id": 244, "name": "a pale green cloak",           "slot": "shoulders"},
            {"item_id": 352, "name": "some flowing robes",           "slot": "torso"},
            {"item_id": 101, "name": "a wooden runestaff",           "hand": "right"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "pouch"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "pouch"},
            {"item_id": 602, "name": "some wolifrew lichen",         "container": "pouch"},
            {"item_id": 603, "name": "some torban leaf",             "container": "pouch"},
            {"item_id": 604, "name": "some woth flower",             "container": "pouch"},
            {"item_id": 605, "name": "some basal moss",              "container": "pouch"},
            {"item_id": 606, "name": "some ambrominas leaf",         "container": "pouch"},
            {"item_id": 607, "name": "some haphip root",             "container": "backpack"},
            {"item_id": 608, "name": "some cactacae spine",          "container": "backpack"},
            {"item_id": 609, "name": "some aloeas stem",             "container": "backpack"},
        ],
    },
    6: {  # SORCERER
        "description": "Sorcerer Starter Kit",
        "items": [
            {"item_id": 236, "name": "a leather backpack",           "slot": "back"},
            {"item_id": 239, "name": "a herb pouch",                 "slot": "belt"},
            {"item_id": 245, "name": "a dark silk cloak",            "slot": "shoulders"},
            {"item_id": 352, "name": "some flowing robes",           "slot": "torso"},
            {"item_id": 101, "name": "a wooden runestaff",           "hand": "right"},
            {"item_id": 750, "name": "a copper symbol",              "container": "backpack"},
            {"item_id": 752, "name": "a vaalin stylus",              "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
        ],
    },
    7: {  # RANGER
        "description": "Ranger Starter Kit",
        "items": [
            {"item_id": 236, "name": "a leather backpack",           "slot": "back"},
            {"item_id": 238, "name": "a belt pouch",                 "slot": "belt"},
            {"item_id": 246, "name": "a forest green cloak",         "slot": "shoulders"},
            {"item_id": 73,  "name": "some light leather armor",     "slot": "torso"},
            {"item_id": 7,   "name": "a steel short sword",          "hand": "right"},
            {"item_id": 201, "name": "a short bow",                  "container": "backpack"},
            {"item_id": 211, "name": "a bundle of arrows",           "container": "backpack"},
            {"item_id": 211, "name": "a bundle of arrows",           "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 602, "name": "some wolifrew lichen",         "container": "pouch"},
        ],
    },
    8: {  # BARD
        "description": "Bard Starter Kit",
        "items": [
            {"item_id": 236, "name": "a leather backpack",           "slot": "back"},
            {"item_id": 238, "name": "a belt pouch",                 "slot": "belt"},
            {"item_id": 247, "name": "a colorful traveling cloak",   "slot": "shoulders"},
            {"item_id": 74,  "name": "some full leather armor",      "slot": "torso"},
            {"item_id": 7,   "name": "a steel short sword",          "hand": "right"},
            {"item_id": 760, "name": "a simple wooden lute",         "container": "backpack"},
            {"item_id": 2,   "name": "a steel dagger",               "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
        ],
    },
    9: {  # PALADIN
        "description": "Paladin Starter Kit",
        "items": [
            {"item_id": 236, "name": "a leather backpack",           "slot": "back"},
            {"item_id": 238, "name": "a belt pouch",                 "slot": "belt"},
            {"item_id": 248, "name": "a white tabard cloak",         "slot": "shoulders"},
            {"item_id": 75,  "name": "some reinforced leather armor","slot": "torso"},
            {"item_id": 94,  "name": "a steel target shield",        "slot": "shoulder_slung"},
            {"item_id": 12,  "name": "a steel broadsword",           "hand": "right"},
            {"item_id": 751, "name": "a holy symbol",                "container": "pouch"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 602, "name": "some wolifrew lichen",         "container": "backpack"},
        ],
    },
    10: {  # MONK
        "description": "Monk Starter Kit",
        "items": [
            {"item_id": 236, "name": "a leather backpack",           "slot": "back"},
            {"item_id": 238, "name": "a belt pouch",                 "slot": "belt"},
            {"item_id": 249, "name": "a rough-spun monk's cloak",    "slot": "shoulders"},
            {"item_id": 353, "name": "some padded armor",            "slot": "torso"},
            {"item_id": 302, "name": "a steel cestus",               "hand": "right"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
            {"item_id": 601, "name": "some acantha leaf",            "container": "backpack"},
        ],
    },
}


def get_starter_gear(profession_id):
    """Get starter gear config for a profession. Returns dict or None."""
    return STARTER_GEAR.get(profession_id)


def get_starting_silver(profession_id):
    """Get starting silver for a profession."""
    return STARTING_SILVER.get(profession_id, 500)


def get_starting_hands(profession_id):
    """Deprecated shim — hand placement is now in the items list (hand='right'/'left')."""
    return {}
