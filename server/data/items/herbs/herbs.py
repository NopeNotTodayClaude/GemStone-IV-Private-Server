"""
GemStone IV Herb Data

All healing herbs from GemStone IV with accurate properties.
Herbs heal specific wound types and severity levels.
Found from foraging, shops, and creature drops.

Heal types: health, head, neck, chest, abdomen, back, left_leg, right_leg,
            left_arm, right_arm, left_hand, right_hand, left_eye, right_eye,
            nerves, blood, scars

Severity levels: 1 (minor), 2 (moderate), 3 (severe)
"""

HERBS = {
    # --- Basic Healing Herbs (General HP) ---
    "sprig of acantha leaf": {
        "base_name": "sprig of acantha leaf",
        "type": "herb",
        "herb_heal_type": "health",
        "herb_heal_amount": 10,
        "herb_severity": 1,
        "weight": 1,
        "value": 50,
        "description": "a sprig of acantha leaf",
    },
    "stem of ambrominas leaf": {
        "base_name": "stem of ambrominas leaf",
        "type": "herb",
        "herb_heal_type": "health",
        "herb_heal_amount": 25,
        "herb_severity": 2,
        "weight": 1,
        "value": 200,
        "description": "a stem of ambrominas leaf",
    },

    # --- Head/Neck Herbs ---
    "sprig of cactacae spine": {
        "base_name": "sprig of cactacae spine",
        "type": "herb",
        "herb_heal_type": "head",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 100,
        "description": "a sprig of cactacae spine",
    },
    "some wolifrew lichen": {
        "base_name": "some wolifrew lichen",
        "type": "herb",
        "herb_heal_type": "head",
        "herb_heal_amount": 0,
        "herb_severity": 2,
        "weight": 1,
        "value": 300,
        "description": "some wolifrew lichen",
    },
    "sprig of torban leaf": {
        "base_name": "sprig of torban leaf",
        "type": "herb",
        "herb_heal_type": "neck",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 100,
        "description": "a sprig of torban leaf",
    },

    # --- Chest/Abdomen Herbs ---
    "some pothinir grass": {
        "base_name": "some pothinir grass",
        "type": "herb",
        "herb_heal_type": "chest",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 100,
        "description": "some pothinir grass",
    },
    "some brostheras potion": {
        "base_name": "some brostheras potion",
        "type": "herb",
        "herb_heal_type": "chest",
        "herb_heal_amount": 0,
        "herb_severity": 2,
        "weight": 1,
        "value": 300,
        "description": "some brostheras potion",
    },
    "some woth flower": {
        "base_name": "some woth flower",
        "type": "herb",
        "herb_heal_type": "abdomen",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 100,
        "description": "some woth flower",
    },

    # --- Limb Herbs ---
    "some ephlox moss": {
        "base_name": "some ephlox moss",
        "type": "herb",
        "herb_heal_type": "right_leg",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 75,
        "description": "some ephlox moss",
    },
    "some haphip root": {
        "base_name": "some haphip root",
        "type": "herb",
        "herb_heal_type": "left_arm",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 75,
        "description": "some haphip root",
    },
    "sprig of aloeas stem": {
        "base_name": "sprig of aloeas stem",
        "type": "herb",
        "herb_heal_type": "left_leg",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 75,
        "description": "a sprig of aloeas stem",
    },
    "some basal moss": {
        "base_name": "some basal moss",
        "type": "herb",
        "herb_heal_type": "right_arm",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 75,
        "description": "some basal moss",
    },

    # --- Eye Herbs ---
    "some rose-marrow potion": {
        "base_name": "some rose-marrow potion",
        "type": "herb",
        "herb_heal_type": "right_eye",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 200,
        "description": "some rose-marrow potion",
    },
    "some sovyn clove": {
        "base_name": "some sovyn clove",
        "type": "herb",
        "herb_heal_type": "left_eye",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 200,
        "description": "some sovyn clove",
    },

    # --- Blood/Nerve Herbs ---
    "some wingstem potion": {
        "base_name": "some wingstem potion",
        "type": "herb",
        "herb_heal_type": "nerves",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 300,
        "description": "some wingstem potion",
    },
    "some bolmara potion": {
        "base_name": "some bolmara potion",
        "type": "herb",
        "herb_heal_type": "nerves",
        "herb_heal_amount": 0,
        "herb_severity": 2,
        "weight": 1,
        "value": 600,
        "description": "some bolmara potion",
    },
    "some redite ore": {
        "base_name": "some red ite ore",
        "type": "herb",
        "herb_heal_type": "blood",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 250,
        "description": "some red ite ore",
    },

    # --- Scar Herbs ---
    "some troll's blood potion": {
        "base_name": "some troll's blood potion",
        "type": "herb",
        "herb_heal_type": "scars",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 500,
        "description": "some troll's blood potion",
    },

    # --- Back Herbs ---
    "some talneo potion": {
        "base_name": "some talneo potion",
        "type": "herb",
        "herb_heal_type": "back",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 100,
        "description": "some talneo potion",
    },

    # --- Hand Herbs ---
    "some calamia fruit": {
        "base_name": "some calamia fruit",
        "type": "herb",
        "herb_heal_type": "left_hand",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 75,
        "description": "some calamia fruit",
    },
    "some tkaro root": {
        "base_name": "some tkaro root",
        "type": "herb",
        "herb_heal_type": "right_hand",
        "herb_heal_amount": 0,
        "herb_severity": 1,
        "weight": 1,
        "value": 75,
        "description": "some tkaro root",
    },

    # --- Multi-purpose / Special Herbs ---
    "some yabathilium fruit": {
        "base_name": "some yabathilium fruit",
        "type": "herb",
        "herb_heal_type": "health",
        "herb_heal_amount": 50,
        "herb_severity": 3,
        "weight": 1,
        "value": 750,
        "description": "some yabathilium fruit",
    },
    "some cuctucae berry": {
        "base_name": "some cuctucae berry",
        "type": "herb",
        "herb_heal_type": "health",
        "herb_heal_amount": 15,
        "herb_severity": 1,
        "weight": 1,
        "value": 75,
        "description": "some cuctucae berry",
    },
    "some wekaf berries": {
        "base_name": "some wekaf berries",
        "type": "herb",
        "herb_heal_type": "health",
        "herb_heal_amount": 5,
        "herb_severity": 1,
        "weight": 1,
        "value": 25,
        "description": "some wekaf berries",
    },
}

# Herb tiers for treasure/foraging based on area level
HERB_TIERS = {
    1: [name for name, h in HERBS.items() if h["value"] <= 100],
    2: [name for name, h in HERBS.items() if 100 < h["value"] <= 300],
    3: [name for name, h in HERBS.items() if h["value"] > 300],
}
