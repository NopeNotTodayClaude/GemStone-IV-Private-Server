#!/usr/bin/env python3
"""
Ta'Vaalor Item Generator
========================
Generates the full item catalog by cross-multiplying:
  - ~70 weapon base forms × ~23 materials      → ~1 400 weapons
  - 20 armor ASG types × appropriate materials  →  ~400 armors
  - 20 shield types × appropriate materials     →  ~200 shields
  - 68 gems, 24 herbs, containers, skins,
    clothing, food, misc                        →  ~400 misc

Run:
    python3 generate_items.py > database/seeds/items/seed_items_generated.sql
"""

import math, sys

# ---------------------------------------------------------------------------
# MATERIALS
# ---------------------------------------------------------------------------
# wt_mult  : weight multiplier vs steel baseline
# val_mult : base value multiplier
# enchant  : inherent enchant bonus of the material
# article  : grammatical article
# avail    : shop availability tier  (1=common, 2=uncommon, 3=rare, 4=legendary)
# ---------------------------------------------------------------------------
METALS = {
    'iron':     {'wt': 1.20, 'val': 0.50, 'enc': 0,  'art': 'an', 'avail': 1},
    'copper':   {'wt': 1.00, 'val': 0.40, 'enc': 0,  'art': 'a',  'avail': 1},
    'bronze':   {'wt': 1.10, 'val': 0.70, 'enc': 0,  'art': 'a',  'avail': 1},
    'steel':    {'wt': 1.00, 'val': 1.00, 'enc': 0,  'art': 'a',  'avail': 1},
    'silver':   {'wt': 0.90, 'val': 3.00, 'enc': 0,  'art': 'a',  'avail': 2},
    'gold':     {'wt': 1.30, 'val': 5.00, 'enc': 0,  'art': 'a',  'avail': 2},
    'mithril':  {'wt': 0.50, 'val': 8.00, 'enc': 0,  'art': 'a',  'avail': 2},
    'vultite':  {'wt': 0.60, 'val': 10.0, 'enc': 5,  'art': 'a',  'avail': 2},
    'vaalorn':  {'wt': 0.80, 'val': 12.0, 'enc': 5,  'art': 'a',  'avail': 2},
    'imflass':  {'wt': 0.50, 'val': 9.00, 'enc': 5,  'art': 'an', 'avail': 2},
    'ora':      {'wt': 0.70, 'val': 8.00, 'enc': 5,  'art': 'an', 'avail': 2},
    'kelyn':    {'wt': 0.40, 'val': 14.0, 'enc': 10, 'art': 'a',  'avail': 3},
    'rolaren':  {'wt': 0.50, 'val': 18.0, 'enc': 10, 'art': 'a',  'avail': 3},
    'glaes':    {'wt': 0.30, 'val': 20.0, 'enc': 15, 'art': 'a',  'avail': 3},
    'alum':     {'wt': 0.40, 'val': 11.0, 'enc': 10, 'art': 'an', 'avail': 3},
    'invar':    {'wt': 0.70, 'val': 12.0, 'enc': 10, 'art': 'an', 'avail': 3},
    'laje':     {'wt': 0.40, 'val': 16.0, 'enc': 15, 'art': 'a',  'avail': 3},
    'eonake':   {'wt': 0.30, 'val': 28.0, 'enc': 20, 'art': 'an', 'avail': 3},
    'eahnor':   {'wt': 0.40, 'val': 35.0, 'enc': 25, 'art': 'an', 'avail': 4},
    'faenor':   {'wt': 0.20, 'val': 40.0, 'enc': 25, 'art': 'a',  'avail': 4},
    'veniom':   {'wt': 0.10, 'val': 60.0, 'enc': 30, 'art': 'a',  'avail': 4},
    'razern':   {'wt': 0.50, 'val': 30.0, 'enc': 20, 'art': 'a',  'avail': 4},
    'eog':      {'wt': 0.30, 'val': 55.0, 'enc': 35, 'art': 'an', 'avail': 4},
}

WOODS = {
    'oak':       {'wt': 1.00, 'val': 0.50, 'enc': 0,  'art': 'an', 'avail': 1},
    'yew':       {'wt': 0.90, 'val': 0.80, 'enc': 0,  'art': 'a',  'avail': 1},
    'hawthorn':  {'wt': 0.90, 'val': 1.50, 'enc': 0,  'art': 'a',  'avail': 1},
    'haon':      {'wt': 0.80, 'val': 2.00, 'enc': 5,  'art': 'a',  'avail': 2},
    'ironwood':  {'wt': 1.20, 'val': 3.00, 'enc': 5,  'art': 'an', 'avail': 2},
    'carmiln':   {'wt': 0.60, 'val': 5.00, 'enc': 10, 'art': 'a',  'avail': 2},
    'kakore':    {'wt': 0.50, 'val': 8.00, 'enc': 15, 'art': 'a',  'avail': 3},
    'villswood': {'wt': 0.40, 'val': 12.0, 'enc': 20, 'art': 'a',  'avail': 3},
    'mossbark':  {'wt': 0.40, 'val': 10.0, 'enc': 15, 'art': 'a',  'avail': 3},
    'orase':     {'wt': 0.30, 'val': 15.0, 'enc': 25, 'art': 'an', 'avail': 4},
    'ruic':      {'wt': 0.30, 'val': 18.0, 'enc': 30, 'art': 'a',  'avail': 4},
}

LEATHERS = {
    'leather':            {'wt': 1.00, 'val': 0.50, 'enc': 0, 'art': 'a',  'avail': 1},
    'dark leather':       {'wt': 0.90, 'val': 1.20, 'enc': 0, 'art': 'a',  'avail': 1},
    'reinforced leather': {'wt': 1.10, 'val': 2.00, 'enc': 5, 'art': 'a',  'avail': 2},
}

CLOTHS = {
    'linen':   {'wt': 0.30, 'val': 0.20, 'art': 'a'},
    'wool':    {'wt': 0.40, 'val': 0.30, 'art': 'a'},
    'cotton':  {'wt': 0.25, 'val': 0.40, 'art': 'a'},
    'silk':    {'wt': 0.20, 'val': 2.00, 'art': 'a'},
    'velvet':  {'wt': 0.35, 'val': 3.00, 'art': 'a'},
    'satin':   {'wt': 0.25, 'val': 2.50, 'art': 'a'},
    'brocade': {'wt': 0.40, 'val': 4.00, 'art': 'a'},
}

# ---------------------------------------------------------------------------
# WEAPON BASE FORMS
# columns: (base_name, noun, category, damage_types, dmg_factor,
#            speed, base_wt, base_val, mat_type)
#   mat_type: 'metal' | 'wood' | 'leather'
# ---------------------------------------------------------------------------
WEAPON_FORMS = [
    # ---- EDGED ----
    ('dagger',          'dagger',         'edged',    'slash,puncture',       0.250, 1, 1.0,   50, 'metal'),
    ('main gauche',     'gauche',         'edged',    'slash,puncture',       0.275, 2, 2.0,  120, 'metal'),
    ('poignard',        'poignard',       'edged',    'puncture',             0.225, 1, 1.0,   40, 'metal'),
    ('rapier',          'rapier',         'edged',    'slash,puncture',       0.325, 2, 2.5,  200, 'metal'),
    ('whip-blade',      'whip-blade',     'edged',    'slash',                0.333, 2, 3.0,  350, 'metal'),
    ('katar',           'katar',          'edged',    'slash,puncture',       0.325, 3, 2.5,  180, 'metal'),
    ('short sword',     'sword',          'edged',    'slash,puncture,crush', 0.350, 3, 3.0,  150, 'metal'),
    ('scimitar',        'scimitar',       'edged',    'slash,puncture,crush', 0.375, 4, 3.5,  250, 'metal'),
    ('estoc',           'estoc',          'edged',    'slash,puncture',       0.425, 4, 4.0,  400, 'metal'),
    ('longsword',       'longsword',      'edged',    'slash,puncture,crush', 0.425, 4, 4.0,  300, 'metal'),
    ('handaxe',         'handaxe',        'edged',    'slash,crush',          0.420, 5, 4.5,  200, 'metal'),
    ('backsword',       'backsword',      'edged',    'slash,puncture,crush', 0.440, 5, 4.5,  350, 'metal'),
    ('broadsword',      'broadsword',     'edged',    'slash,puncture,crush', 0.450, 5, 5.0,  400, 'metal'),
    ('falchion',        'falchion',       'edged',    'slash,crush',          0.450, 5, 5.0,  380, 'metal'),
    ('katana',          'katana',         'edged',    'slash',                0.450, 5, 4.0,  600, 'metal'),
    ('bastard sword',   'sword',          'edged',    'slash,crush',          0.450, 6, 5.5,  500, 'metal'),
    ('double-bit axe',  'axe',            'edged',    'slash',                0.475, 6, 7.0,  350, 'metal'),
    # ---- BLUNT ----
    ('cudgel',          'cudgel',         'blunt',    'crush',                0.300, 3, 4.0,   50, 'metal'),
    ('mace',            'mace',           'blunt',    'crush',                0.350, 4, 5.0,  150, 'metal'),
    ('flail',           'flail',          'blunt',    'crush',                0.375, 5, 5.5,  250, 'metal'),
    ('morning star',    'star',           'blunt',    'crush,puncture',       0.400, 5, 6.0,  300, 'metal'),
    ('war hammer',      'hammer',         'blunt',    'crush',                0.425, 5, 6.0,  350, 'metal'),
    ('ball and chain',  'chain',          'blunt',    'crush',                0.450, 6, 7.0,  400, 'metal'),
    ('quarterstaff',    'quarterstaff',   'blunt',    'crush',                0.250, 3, 3.0,   25, 'wood'),
    # ---- TWO-HANDED ----
    ('claymore',        'claymore',       'twohanded','slash,crush',          0.500, 7,  8.0,  500, 'metal'),
    ('flamberge',       'flamberge',      'twohanded','slash',                0.525, 7,  9.0,  600, 'metal'),
    ('zweihander',      'zweihander',     'twohanded','slash,crush',          0.550, 8, 10.0,  700, 'metal'),
    ('warsword',        'warsword',       'twohanded','slash,crush',          0.575, 7, 10.0,  500, 'metal'),
    ('claidhmore',      'claidhmore',     'twohanded','slash',                0.600, 7, 12.0,  550, 'metal'),
    ('greatsword',      'greatsword',     'twohanded','slash,crush',          0.650, 8, 14.0,  700, 'metal'),
    ('battle axe',      'axe',            'twohanded','slash,crush',          0.500, 7,  8.0,  400, 'metal'),
    ('great axe',       'axe',            'twohanded','slash,crush',          0.550, 8, 10.0,  550, 'metal'),
    ('maul',            'maul',           'twohanded','crush',                0.575, 8, 12.0,  450, 'metal'),
    ('war mattock',     'mattock',        'twohanded','crush,puncture',       0.525, 7, 10.0,  400, 'metal'),
    ('runestaff',       'runestaff',      'twohanded','crush',                0.275, 5,  4.0,  500, 'wood'),
    # ---- POLEARM ----
    ('spear',           'spear',          'polearm',  'puncture',             0.350, 5,  5.0,  100, 'metal'),
    ('pike',            'pike',           'polearm',  'puncture',             0.400, 6,  8.0,  200, 'metal'),
    ('trident',         'trident',        'polearm',  'puncture',             0.400, 5,  6.0,  250, 'metal'),
    ('partisan',        'partisan',       'polearm',  'slash,puncture',       0.425, 6,  7.0,  300, 'metal'),
    ('glaive',          'glaive',         'polearm',  'slash',                0.450, 6,  7.0,  350, 'metal'),
    ('naginata',        'naginata',       'polearm',  'slash',                0.425, 5,  6.0,  400, 'metal'),
    ('javelin',         'javelin',        'polearm',  'puncture',             0.300, 4,  3.0,   75, 'metal'),
    ('awl-pike',        'awl-pike',       'polearm',  'puncture',             0.450, 7,  9.0,  250, 'metal'),
    ('voulge',          'voulge',         'polearm',  'slash,crush',          0.450, 6,  8.0,  300, 'metal'),
    ('halberd',         'halberd',        'polearm',  'slash,puncture,crush', 0.525, 7,  9.0,  500, 'metal'),
    ('lance',           'lance',          'polearm',  'puncture',             0.475, 7, 10.0,  350, 'metal'),
    # ---- RANGED ----
    ('short bow',       'bow',            'ranged',   'puncture',             0.250, 4, 2.0,  100, 'wood'),
    ('long bow',        'bow',            'ranged',   'puncture',             0.350, 5, 3.0,  250, 'wood'),
    ('composite bow',   'bow',            'ranged',   'puncture',             0.400, 5, 3.0,  400, 'wood'),
    ('light crossbow',  'crossbow',       'ranged',   'puncture',             0.400, 6, 4.0,  300, 'metal'),
    ('heavy crossbow',  'crossbow',       'ranged',   'puncture',             0.500, 8, 7.0,  500, 'metal'),
    ('hand crossbow',   'crossbow',       'ranged',   'puncture',             0.250, 4, 2.0,  200, 'wood'),
    # ---- THROWN ----
    ('throwing dagger', 'dagger',         'thrown',   'puncture',             0.200, 2, 1.0,   30, 'metal'),
    ('throwing axe',    'axe',            'thrown',   'slash,crush',          0.300, 3, 3.0,   75, 'metal'),
    ('dart',            'dart',           'thrown',   'puncture',             0.150, 2, 0.5,   15, 'metal'),
    ('shuriken',        'shuriken',       'thrown',   'slash,puncture',       0.175, 2, 0.5,   50, 'metal'),
    ('throwing hammer', 'hammer',         'thrown',   'crush',                0.350, 4, 4.0,  100, 'metal'),
    ('discus',          'discus',         'thrown',   'slash',                0.350, 3, 2.0,  100, 'metal'),
    ('quoit',           'quoit',          'thrown',   'slash',                0.300, 2, 1.5,   80, 'metal'),
    # ---- BRAWLING ----
    ('cestus',          'cestus',         'brawling', 'crush',                0.200, 2, 1.0,   50, 'leather'),
    ('knuckle-dusters', 'knuckle-dusters','brawling', 'crush',                0.225, 2, 1.0,   75, 'metal'),
    ('hook-knife',      'hook-knife',     'brawling', 'slash,puncture',       0.250, 2, 1.0,  100, 'metal'),
    ('paingrips',       'paingrips',      'brawling', 'crush,puncture',       0.275, 3, 1.5,  150, 'metal'),
    ('tiger-claw',      'tiger-claw',     'brawling', 'slash',                0.275, 2, 1.0,  200, 'metal'),
    ('fist-scythe',     'fist-scythe',    'brawling', 'slash',                0.275, 3, 1.5,  175, 'metal'),
    ('troll-claws',     'troll-claws',    'brawling', 'slash,puncture',       0.300, 3, 2.0,  250, 'metal'),
    ('yierka-spur',     'yierka-spur',    'brawling', 'puncture',             0.250, 2, 1.0,  125, 'metal'),
    ('hand wraps',      'wraps',          'brawling', 'crush',                0.150, 2, 0.5,   15, 'leather'),
    ('knuckle-blade',   'knuckle-blade',  'brawling', 'slash,puncture',       0.275, 2, 1.0,  200, 'metal'),
    ('razorpaws',       'razorpaws',      'brawling', 'slash',                0.275, 3, 1.5,  225, 'metal'),
    ('spiked gauntlet', 'gauntlet',       'brawling', 'crush,puncture',       0.275, 3, 2.0,  175, 'metal'),
    ('claw gauntlet',   'gauntlet',       'brawling', 'slash',                0.300, 3, 2.0,  200, 'metal'),
]

# ---------------------------------------------------------------------------
# ARMOR  (asg, display_name, noun, base_weight, base_value,
#          cva, action_penalty, spell_hindrance, mat_type)
# mat_type: 'cloth' | 'leather' | 'metal' | 'any_metal'
# ---------------------------------------------------------------------------
ARMOR_FORMS = [
    # cloth / light
    (1,  'normal clothing',    'clothing',   2.0,   10,  25, 0,  0, 'cloth'),
    (2,  'flowing robes',      'robes',      3.0,   50,  25, 0,  0, 'cloth'),
    (3,  'padded armor',       'armor',      4.0,   75,  24, 0,  0, 'cloth'),
    # leather
    (4,  'light leather armor','armor',      5.0,  100,  22, 0,  1, 'leather_armor'),
    (5,  'full leather armor', 'armor',      7.0,  200,  20, 0,  3, 'leather_armor'),
    (6,  'reinforced leather', 'leather',    8.0,  300,  18, 0,  5, 'leather_armor'),
    (7,  'double leather',     'leather',   10.0,  400,  16, 2,  8, 'leather_armor'),
    (8,  'leather breastplate','breastplate',12.0,  500,  14, 5, 10, 'leather_armor'),
    (9,  'studded leather',    'armor',     13.0,  600,  13, 5, 12, 'leather_armor'),
    # metal light
    (10, 'brigandine armor',   'armor',     14.0,  700,  12, 7, 14, 'metal'),
    (11, 'chain mail',         'mail',      16.0,  800,  10, 7, 15, 'metal'),
    (12, 'double chain mail',  'mail',      20.0, 1000,   8,10, 18, 'metal'),
    (13, 'augmented chain',    'chain',     22.0, 1200,   5,12, 20, 'metal'),
    (14, 'chain hauberk',      'hauberk',   25.0, 1500,   3,13, 22, 'metal'),
    # metal heavy
    (15, 'metal breastplate',  'breastplate',20.0, 1800,  1,14, 25, 'metal'),
    (16, 'augmented breastplate','breastplate',25.0,2200,-2,16, 27, 'metal'),
    (17, 'half plate',         'plate',     30.0, 3000,  -5,18, 30, 'metal'),
    (18, 'full plate',         'plate',     35.0, 4000,  -8,20, 33, 'metal'),
    (19, 'augmented plate',    'plate',     40.0, 5000, -10,22, 35, 'metal'),
    (20, 'razern plate',       'plate',     45.0, 8000, -12,25, 38, 'metal'),
]

# ---------------------------------------------------------------------------
# SHIELDS (name, noun, size, base_ds, evade_pen, base_wt, base_val, mat_type)
# ---------------------------------------------------------------------------
SHIELD_FORMS = [
    # small
    ('buckler',          'buckler',  'small',  10, 2,  3.0,  150, 'metal'),
    ('target shield',    'shield',   'small',  12, 3,  4.0,  175, 'metal'),
    ('small shield',     'shield',   'small',  13, 4,  5.0,  200, 'metal'),
    # medium
    ('heater shield',    'shield',   'medium', 18, 7,  7.0,  350, 'metal'),
    ("knight's shield",  'shield',   'medium', 19, 8,  8.0,  500, 'metal'),
    ('medium shield',    'shield',   'medium', 16, 7,  7.0,  300, 'metal'),
    # large
    ('kite shield',      'shield',   'large',  24,14, 11.0,  600, 'metal'),
    ('mantlet',          'mantlet',  'large',  25,15, 12.0,  750, 'metal'),
    ('large shield',     'shield',   'large',  22,13, 10.0,  500, 'metal'),
    # tower
    ('tower shield',     'shield',   'tower',  30,22, 16.0, 1200, 'metal'),
    ('pavise',           'pavise',   'tower',  31,24, 18.0, 1400, 'metal'),
    ('wall shield',      'shield',   'tower',  33,26, 20.0, 1800, 'metal'),
]

# ---------------------------------------------------------------------------
# GEMS (no generator needed - list directly)
# ---------------------------------------------------------------------------
GEMS = [
    # (name, noun, gem_family, value)
    ('a piece of blue ridge coral',  'coral',      'agate',    25),
    ('a blood marble',               'marble',     'agate',    50),
    ("a piece of cat's eye quartz",  'quartz',     'agate',    50),
    ('a tigerfang crystal',          'crystal',    'agate',    75),
    ('a turquoise stone',            'stone',      'agate',   100),
    ('a leopard quartz',             'quartz',     'agate',   100),
    ('a piece of golden amber',      'amber',      'agate',   125),
    ('a smoky topaz',                'topaz',      'agate',   150),
    ('a blue lace agate',            'agate',      'agate',    50),
    ('a sardonyx stone',             'stone',      'agate',    75),
    ('a small golden topaz',         'topaz',      'beryl',   350),
    ('a pink topaz',                 'topaz',      'beryl',   500),
    ('an aquamarine gem',            'gem',        'beryl',   500),
    ('a green malachite stone',      'stone',      'beryl',   200),
    ('a golden beryl gem',           'gem',        'beryl',   600),
    ('a green beryl stone',          'stone',      'beryl',   350),
    ('a dark red-green bloodstone',  'bloodstone', 'carbuncle',200),
    ('a deep red carbuncle',         'carbuncle',  'carbuncle',350),
    ('a red carbuncle',              'carbuncle',  'carbuncle',300),
    ('a violet sapphire',            'sapphire',   'cordierite',1000),
    ('a blue sapphire',              'sapphire',   'cordierite',1000),
    ('a star sapphire',              'sapphire',   'cordierite',1500),
    ('a pale blue moonstone',        'moonstone',  'cordierite',150),
    ('a blue cordierite',            'cordierite', 'cordierite',300),
    ('an uncut diamond',             'diamond',    'diamond', 2500),
    ('a white crystal',              'crystal',    'diamond',   75),
    ('a clear zircon',               'zircon',     'diamond',  200),
    ('a rock crystal',               'crystal',    'diamond',  100),
    ('a white opal',                 'opal',       'diamond',  400),
    ('an emerald',                   'emerald',    'emerald', 2000),
    ('a green aventurine stone',     'stone',      'emerald',  100),
    ('a green jade',                 'jade',       'emerald',  350),
    ('a green tourmaline',           'tourmaline', 'emerald',  500),
    ('a green garnet',               'garnet',     'emerald',  600),
    ('a green chrysoberyl gem',      'gem',        'emerald',  400),
    ('a peridot',                    'peridot',    'emerald',  250),
    ('a dark red garnet',            'garnet',     'garnet',   300),
    ('a red spinel',                 'spinel',     'garnet',   400),
    ('a star ruby',                  'ruby',       'garnet',  1500),
    ('a ruby',                       'ruby',       'garnet',  2000),
    ('a fire opal',                  'opal',       'garnet',   800),
    ('an almandine garnet',          'garnet',     'garnet',   500),
    ('some lapis lazuli',            'lazuli',     'lapis',    200),
    ('some azurite',                 'azurite',    'lapis',     75),
    ('a shimmertine shard',          'shard',      'lapis',    150),
    ('a blue tourmaline',            'tourmaline', 'lapis',    400),
    ('some obsidian',                'obsidian',   'obsidian',  25),
    ('a black opal',                 'opal',       'obsidian', 1000),
    ('a jet black onyx',             'onyx',       'obsidian',  250),
    ('a piece of black hematite',    'hematite',   'obsidian',   50),
    ('a clear quartz',               'quartz',     'quartz',    50),
    ('a rose quartz',                'quartz',     'quartz',    75),
    ('a citrine quartz',             'quartz',     'quartz',   100),
    ('an amethyst',                  'amethyst',   'quartz',   200),
    ('a smoky quartz',               'quartz',     'quartz',    75),
    ('a small white pearl',          'pearl',      'pearl',    150),
    ('a large white pearl',          'pearl',      'pearl',    350),
    ('a pink pearl',                 'pearl',      'pearl',    500),
    ('a black pearl',                'pearl',      'pearl',    800),
    ('a golden pearl',               'pearl',      'pearl',    600),
    ('a chrysoberyl gem',            'gem',        'misc',     300),
    ('an alexandrite stone',         'stone',      'misc',    1500),
    ('a piece of jasper',            'jasper',     'misc',      75),
    ('a piece of carnelian quartz',  'quartz',     'misc',     100),
    ('an aventurine',                'aventurine', 'misc',     100),
    ('an ametrine gem',              'gem',        'misc',     250),
    ('an opal',                      'opal',       'misc',     400),
    ('a dragonfire opal',            'opal',       'misc',    2000),
    ('a moonstone',                  'moonstone',  'misc',     150),
    ('a sunstone',                   'sunstone',   'misc',     200),
    ('a piece of jade',              'jade',       'misc',     250),
    ('an uncut ruby',                'ruby',       'garnet',  1500),
    ('an uncut emerald',             'emerald',    'emerald', 1500),
]

# ---------------------------------------------------------------------------
# HERBS
# ---------------------------------------------------------------------------
HERBS = [
    # (name, noun, heal_type, heal_amount, value)
    ('a sprig of acantha leaf',         'leaf',    'health',     10, 50),
    ('a stem of ambrominas leaf',       'leaf',    'health',     25, 200),
    ('a sprig of cactacae spine',       'spine',   'head',        0, 100),
    ('some wolifrew lichen',            'lichen',  'head',        0, 300),
    ('a sprig of torban leaf',          'leaf',    'neck',        0, 100),
    ('some pothinir grass',             'grass',   'chest',       0, 100),
    ('some brostheras potion',          'potion',  'chest',       0, 300),
    ('some woth flower',                'flower',  'abdomen',     0, 100),
    ('some ephlox moss',                'moss',    'right_leg',   0, 75),
    ('some haphip root',                'root',    'left_arm',    0, 75),
    ('a sprig of aloeas stem',          'stem',    'left_leg',    0, 75),
    ('some basal moss',                 'moss',    'right_arm',   0, 75),
    ('some rose-marrow potion',         'potion',  'right_eye',   0, 200),
    ('some sovyn clove',                'clove',   'left_eye',    0, 200),
    ('some wingstem potion',            'potion',  'nerves',      0, 300),
    ('some bolmara potion',             'potion',  'nerves',      0, 600),
    ('some redite ore',                 'ore',     'blood',       0, 250),
    ("some troll's blood potion",       'potion',  'scars',       0, 500),
    ('some talneo potion',              'potion',  'back',        0, 100),
    ('some calamia fruit',              'fruit',   'left_hand',   0, 75),
    ('some tkaro root',                 'root',    'right_hand',  0, 75),
    ('some yabathilium fruit',          'fruit',   'health',     50, 750),
    ('some cuctucae berry',             'berry',   'health',     15, 75),
    ('some wekaf berries',              'berries', 'health',      5, 25),
]

# ---------------------------------------------------------------------------
# LOCKPICKS
# ---------------------------------------------------------------------------
LOCKPICKS = [
    # (name, noun, material, modifier, value)
    ('a crude lockpick',          'lockpick', None,       5.00,   50),
    ('a simple lockpick',         'lockpick', None,      10.00,  100),
    ('a standard lockpick',       'lockpick', None,      15.00,  200),
    ('a professional lockpick',   'lockpick', None,      20.00,  400),
    ("a master's lockpick",       'lockpick', None,      25.00,  800),
    ('a copper lockpick',         'lockpick', 'copper',  10.00,  150),
    ('a bronze lockpick',         'lockpick', 'bronze',  15.00,  250),
    ('a steel lockpick',          'lockpick', 'steel',   20.00,  500),
    ('a mithril lockpick',        'lockpick', 'mithril', 30.00, 2000),
    ('a vultite lockpick',        'lockpick', 'vultite', 35.00, 5000),
    ('a laje lockpick',           'lockpick', 'laje',    30.00, 3000),
    ('an ora lockpick',           'lockpick', 'ora',     25.00, 1500),
    ('a veniom lockpick',         'lockpick', 'veniom',  40.00,10000),
    ('a rolaren lockpick',        'lockpick', 'rolaren', 35.00, 7500),
    ('an alum lockpick',          'lockpick', 'alum',    25.00, 1200),
    ('an invar lockpick',         'lockpick', 'invar',   25.00, 1200),
    ('a kelyn lockpick',          'lockpick', 'kelyn',   30.00, 2500),
    ('a glaes lockpick',          'lockpick', 'glaes',   35.00, 6000),
]

# ---------------------------------------------------------------------------
# CREATURE SKINS / DROPS
# ---------------------------------------------------------------------------
CREATURE_DROPS = [
    # (name, noun, item_type, value, creature_source)
    ('a tattered kobold skin',        'skin',     'skin',  10, 'kobold'),
    ('a kobold ear',                  'ear',      'misc',   5, 'kobold'),
    ('a rat pelt',                    'pelt',     'skin',   5, 'giant rat'),
    ('a grey rat tail',               'tail',     'misc',   3, 'giant rat'),
    ('a fanged rodent pelt',          'pelt',     'skin',  12, 'fanged rodent'),
    ('a small rodent fang',           'fang',     'misc',   8, 'fanged rodent'),
    ('a wolf pelt',                   'pelt',     'skin',  50, 'wolf'),
    ('a wolf fang',                   'fang',     'misc',  20, 'wolf'),
    ('a bear skin',                   'skin',     'skin', 100, 'bear'),
    ('a bear claw',                   'claw',     'misc',  35, 'bear'),
    ('a troll hide',                  'hide',     'skin', 150, 'troll'),
    ('a troll fist',                  'fist',     'misc',  50, 'troll'),
    ('a worm skin',                   'skin',     'skin',  75, 'cave worm'),
    ('a worm fang',                   'fang',     'misc',  30, 'cave worm'),
    ('a basilisk skin',               'skin',     'skin', 200, 'basilisk'),
    ('a basilisk eye',                'eye',      'misc',  80, 'basilisk'),
    ('some cockatrice feathers',      'feathers', 'skin', 100, 'cockatrice'),
    ('a cockatrice beak',             'beak',     'misc',  45, 'cockatrice'),
    ('a phantom claw',                'claw',     'misc', 120, 'phantom'),
    ('a spectral essence',            'essence',  'misc', 250, 'spectre'),
    ('a ghoul finger',                'finger',   'misc',  40, 'ghoul'),
    ('a zombie brain',                'brain',    'misc',  30, 'zombie'),
    ('a skeleton knuckle',            'knuckle',  'misc',  15, 'skeleton'),
    ('a catacomb rat pelt',           'pelt',     'skin',  20, 'catacomb rat'),
    ('a rotting shroud',              'shroud',   'misc',  60, 'wraith'),
    ('a shadow thread',               'thread',   'misc', 150, 'shadow'),
    ('a dark crystal shard',          'shard',    'gem',  200, 'dark creature'),
    ('a piece of pale bone',          'bone',     'misc',  10, 'undead'),
    ('a desiccated finger bone',      'bone',     'misc',  25, 'undead'),
    ('a rusted chain link',           'link',     'misc',   5, 'undead'),
    ('a crumbling iron helm',         'helm',     'misc',  30, 'skeleton warrior'),
    ('a void spider web sac',         'sac',      'misc',  90, 'void spider'),
    ('a void spider fang',            'fang',     'misc',  70, 'void spider'),
    ('a myklian scale',               'scale',    'skin', 180, 'myklian'),
    ('a myklian tail tip',            'tip',      'misc', 100, 'myklian'),
    ('an animated armor shard',       'shard',    'misc',  80, 'animated armor'),
    ('a decayed leather patch',       'patch',    'misc',  15, 'undead'),
    ('a cracked burial urn',          'urn',      'misc',  45, 'tomb guardian'),
    ('a tarnished silver locket',     'locket',   'misc', 120, 'ghost'),
    ('a haunted music box',           'box',      'misc', 300, 'banshee'),
]

# ---------------------------------------------------------------------------
# CONTAINERS
# ---------------------------------------------------------------------------
CONTAINERS = [
    # (name, short_name, noun, capacity, weight, value)
    # treasure containers (found as loot, not bought)
    ('a small chest',           'small chest',     'chest',     5,  3,    0),
    ('a medium chest',          'medium chest',    'chest',     8,  5,    0),
    ('a large chest',           'large chest',     'chest',    12,  8,    0),
    ('a metal strongbox',       'metal strongbox', 'strongbox', 5,  6,    0),
    ('an enruned strongbox',    'enruned strongbox','strongbox', 5,  6,    0),
    ('a wooden coffer',         'wooden coffer',   'coffer',    4,  2,    0),
    ('an iron coffer',          'iron coffer',     'coffer',    4,  4,    0),
    ('a mithril coffer',        'mithril coffer',  'coffer',    4,  3,    0),
    ('a small steel lockbox',   'steel lockbox',   'lockbox',   3,  4,    0),
    ('an ornate brass box',     'ornate brass box','box',        4,  3,    0),
    ('a dented iron box',       'dented iron box', 'box',        3,  4,    0),
    ('a heavy steel trunk',     'heavy steel trunk','trunk',    10, 12,    0),
    # wearable/purchasable containers
    ('a small leather pouch',   'small leather pouch', 'pouch',  5,  1,   50),
    ('a leather backpack',      'leather backpack',    'backpack',20, 3,  200),
    ('a large sack',            'large sack',          'sack',  15,  2,   75),
    ('a belt pouch',            'belt pouch',          'pouch',  5,  1,   30),
    ('an herb pouch',           'herb pouch',          'pouch', 10,  1,  100),
    ('a gem pouch',             'gem pouch',           'pouch', 20,  1,  150),
    ("an adventurer's cloak",   "adventurer's cloak",  'cloak', 10,  2,  300),
    ('a weapon harness',        'weapon harness',      'harness', 4, 3,  500),
    ('a small wooden box',      'small wooden box',    'box',    6,  2,   20),
    ("a traveler's pack",       "traveler's pack",     'pack',  25,  4,  400),
    ('a hunting pack',          'hunting pack',        'pack',  30,  5,  600),
    ('a dark leather satchel',  'dark leather satchel','satchel',15, 2,  350),
    ('a canvas haversack',      'canvas haversack',    'haversack',20,3,  250),
    ('a silk coin purse',       'silk coin purse',     'purse',  5,  1,  100),
    ('an embroidered cloak',    'embroidered cloak',   'cloak', 12,  2,  500),
]

# ---------------------------------------------------------------------------
# CLOTHING (misc items worn)
# ---------------------------------------------------------------------------
CLOTHING_BASES = [
    # (noun, worn_location, base_weight, base_value)
    ('cloak',    'shoulders', 1.0, 200),
    ('doublet',  'torso',     1.0, 150),
    ('tunic',    'torso',     0.8, 100),
    ('shirt',    'torso',     0.5,  80),
    ('gown',     'torso',     2.0, 400),
    ('bodice',   'torso',     1.0, 200),
    ('jerkin',   'torso',     1.0, 120),
    ('breeches', 'legs',      1.0,  80),
    ('trousers', 'legs',      0.9,  70),
    ('skirt',    'legs',      1.0, 120),
    ('boots',    'feet',      2.0, 120),
    ('sandals',  'feet',      0.5,  50),
    ('slippers', 'feet',      0.5,  80),
    ('gloves',   'hands',     0.5,  30),
    ('gauntlets','hands',     1.0,  80),
    ('hat',      'head',      0.5,  60),
    ('cap',      'head',      0.3,  40),
    ('hood',     'head',      0.4,  50),
    ('sash',     'waist',     0.3,  40),
    ('belt',     'waist',     0.5,  60),
    ('shawl',    'shoulders', 0.5, 100),
    ('scarf',    'neck',      0.3,  50),
    ('vest',     'torso',     0.6,  90),
    ('robe',     'torso',     2.0, 200),
]

CLOTH_COLORS = [
    'crimson', 'deep blue', 'forest green', 'black', 'white', 'grey',
    'gold', 'silver', 'purple', 'ivory', 'amber', 'emerald',
    'midnight blue', 'dark red', 'pale green', 'russet',
]

# ---------------------------------------------------------------------------
# FOOD & DRINK
# ---------------------------------------------------------------------------
FOOD_ITEMS = [
    # (name, noun, item_type, value, stackable)
    ('a bundle of travel rations',     'rations',    'consumable',  20, 1),
    ('a loaf of elven waybread',       'waybread',   'consumable',  30, 1),
    ('a strip of dried venison',       'venison',    'consumable',  10, 1),
    ('a pouch of trail mix',           'mix',        'consumable',  15, 1),
    ('a meat pie',                     'pie',        'consumable',  10, 1),
    ('a roasted haunch',               'haunch',     'consumable',  15, 0),
    ('a bowl of hearty stew',          'stew',       'consumable',  20, 0),
    ('a honey roll',                   'roll',       'consumable',   5, 1),
    ('a cheese wedge',                 'wedge',      'consumable',   8, 1),
    ('an apple',                       'apple',      'consumable',   3, 1),
    ('a biscuit',                      'biscuit',    'consumable',   3, 1),
    ('a piece of bread',               'bread',      'consumable',   5, 1),
    ('a waterskin',                    'waterskin',  'misc',        25, 0),
    ('a tankard of elven ale',         'ale',        'consumable',  15, 0),
    ('a glass of Vaalor red wine',     'wine',       'consumable',  25, 0),
    ('a mug of dwarven stout',         'stout',      'consumable',  20, 0),
    ('a flask of elven brandy',        'brandy',     'consumable',  50, 0),
    ('a flask of water',               'flask',      'consumable',   5, 0),
    ('a bottle of wine',               'bottle',     'consumable',  25, 0),
    ('a flask of elven spirits',       'flask',      'consumable', 100, 0),
]

# ---------------------------------------------------------------------------
# MISC (tools, lights, scrolls, etc.)
# ---------------------------------------------------------------------------
MISC_ITEMS = [
    # (name, noun, item_type, weight, value)
    ('a wooden torch',                'torch',      'misc',     2,   5),
    ('an oil lantern',                'lantern',    'misc',     3,  50),
    ('a glowing glowbark wand',       'wand',       'misc',     1, 200),
    ('a coil of rope',                'rope',       'misc',     3,  15),
    ('a grappling hook',              'hook',       'misc',     3,  50),
    ('a shovel',                      'shovel',     'misc',     4,  25),
    ('a pickaxe',                     'pickaxe',    'misc',     5,  30),
    ('a fishing pole',                'pole',       'misc',     3,  20),
    ('a pair of tongs',               'tongs',      'misc',     2,  15),
    ('a hammer',                      'hammer',     'misc',     3,  15),
    ('a needle and thread',           'thread',     'misc',     1,   5),
    ('a pair of scissors',            'scissors',   'misc',     1,  10),
    ('a small crystal runestone',     'runestone',  'wand',     1,  50),
    ('a smooth grey runestone',       'runestone',  'wand',     1, 150),
    ('a glowing white runestone',     'runestone',  'wand',     1, 300),
    ('a silver wand',                 'wand',       'wand',     1, 500),
    ('a gold ring',                   'ring',       'jewelry',  1, 200),
    ('a silver ring',                 'ring',       'jewelry',  1,  50),
    ('a gold necklace',               'necklace',   'jewelry',  1, 400),
    ('a silver bracelet',             'bracelet',   'jewelry',  1,  75),
    ('a gold bracelet',               'bracelet',   'jewelry',  1, 300),
    ('a crystal amulet',              'amulet',     'jewelry',  1, 150),
    ('an ivory comb',                 'comb',       'misc',     1,  30),
    ('a set of bone dice',            'dice',       'misc',     1,  10),
    ('a prayer bead necklace',        'necklace',   'misc',     1,  25),
    ('a crinkled minor spirit scroll','scroll',     'scroll',   1, 100),
    ('a weathered major spirit scroll','scroll',    'scroll',   1, 200),
    ('an arcane wizard scroll',       'scroll',     'scroll',   1, 250),
    ('a dark sorcerer scroll',        'scroll',     'scroll',   1, 300),
    ('a blessed cleric scroll',       'scroll',     'scroll',   1, 200),
    ('a glowing empath scroll',       'scroll',     'scroll',   1, 200),
    ('a leaf-bound ranger scroll',    'scroll',     'scroll',   1, 150),
    ('a musical bard scroll',         'scroll',     'scroll',   1, 200),
    ('a radiant paladin scroll',      'scroll',     'scroll',   1, 200),
    # Deeds (very important for the death system)
    ('a deed of Lorminstra',          'deed',       'misc',     1, 500),
    ('a glowing deed of Lorminstra',  'deed',       'misc',     1,1000),
    # Ores (crafting materials)
    ('a chunk of iron ore',           'ore',        'misc',     3,  10),
    ('a chunk of copper ore',         'ore',        'misc',     3,  15),
    ('a chunk of silver ore',         'ore',        'misc',     3,  50),
    ('a chunk of gold ore',           'ore',        'misc',     3, 100),
    ('a chunk of mithril ore',        'ore',        'misc',     2, 500),
    ('a chunk of vultite ore',        'ore',        'misc',     2,1000),
    ('a chunk of ora ore',            'ore',        'misc',     3, 200),
    ('a chunk of imflass ore',        'ore',        'misc',     2, 400),
    ('a chunk of invar ore',          'ore',        'misc',     3, 200),
    ('a chunk of kelyn ore',          'ore',        'misc',     3, 350),
    ('a chunk of rolaren ore',        'ore',        'misc',     2,2000),
    ('a chunk of laje ore',           'ore',        'misc',     2, 800),
    ('a chunk of faenor ore',         'ore',        'misc',     2,3000),
    ('a shard of glaes',              'shard',      'misc',     2,1500),
    ('a chunk of eahnor ore',         'ore',        'misc',     2,5000),
    # Arrows and bolts (ranged ammo)
    ('a bundle of arrows',            'arrows',     'misc',     2,  30),
    ('a bundle of war arrows',        'arrows',     'misc',     2,  60),
    ('a bundle of crossbow bolts',    'bolts',      'misc',     2,  40),
    ('a fletched hunting arrow',      'arrow',      'misc',     1,   3),
    ('a steel-headed war bolt',       'bolt',       'misc',     1,   5),
]

# ---------------------------------------------------------------------------
# SQL HELPERS
# ---------------------------------------------------------------------------

def esc(s):
    if s is None:
        return 'NULL'
    return "'" + str(s).replace("'", "''") + "'"

def num(v):
    if v is None:
        return 'NULL'
    return str(v)

def round2(v):
    return round(float(v), 2)

def article_for(name):
    """Guess article from first letter of name."""
    first = name.lstrip('a ').lstrip('an ').lstrip('some ')
    # If name starts with vowel, use 'an'
    if name[0].lower() in 'aeiou':
        return 'an'
    return 'a'

def weapon_short(mat, base_name):
    return f"{mat} {base_name}"

def weapon_name(mat_art, mat, base_name):
    return f"{mat_art} {mat} {base_name}"

# ---------------------------------------------------------------------------
# GENERATORS
# ---------------------------------------------------------------------------

rows = []  # list of dicts, will be turned into INSERT rows

def add(**kw):
    rows.append(kw)

# ----- WEAPONS --------------------------------------------------------------

for (base_name, noun, cat, dmg_type, dmg_factor, speed, base_wt, base_val, mat_type) in WEAPON_FORMS:
    if mat_type == 'metal':
        materials = METALS
    elif mat_type == 'wood':
        materials = WOODS
    else:  # leather
        materials = LEATHERS

    for mat, mp in materials.items():
        wt  = round2(base_wt * mp['wt'])
        val = max(1, int(base_val * mp['val']))
        enc = mp['enc']
        art = mp['art']
        nm  = f"{art} {mat} {base_name}"
        sn  = f"{mat} {base_name}"

        add(
            name          = nm,
            short_name    = sn,
            base_name     = base_name,
            noun          = noun,
            article       = art,
            item_type     = 'weapon',
            material      = mat,
            weapon_type   = cat,
            weapon_category = cat,
            damage_factor = dmg_factor,
            damage_type   = dmg_type,
            weapon_speed  = speed,
            attack_bonus  = 0,
            damage_bonus  = 0,
            enchant_bonus = enc,
            weight        = wt,
            value         = val,
            is_template   = 1,
            description   = f"A {mat} {base_name}.",
        )

# ----- ARMOR ----------------------------------------------------------------

# Material groupings per armor ASG
CLOTH_TYPES    = CLOTHS
LEATHER_ARMORS = {'leather': {'wt':1.0,'val':0.8},
                  'dark leather':{'wt':0.9,'val':1.2},
                  'reinforced leather':{'wt':1.1,'val':2.0},
                  'boiled leather':{'wt':1.0,'val':1.5},
                  'hardened leather':{'wt':1.2,'val':2.5}}
ARMOR_METALS   = METALS

for (asg, disp_name, noun, base_wt, base_val, cva, act_pen, sp_hind, mat_type) in ARMOR_FORMS:
    if mat_type == 'cloth':
        mat_dict = CLOTH_TYPES
    elif mat_type == 'leather_armor':
        mat_dict = LEATHER_ARMORS
    else:  # metal
        mat_dict = ARMOR_METALS

    for mat, mp in mat_dict.items():
        wt  = round2(base_wt * mp.get('wt', mp.get('wt_mult', 1.0)))
        val = max(1, int(base_val * mp.get('val', mp.get('val_mult', 1.0))))
        enc = mp.get('enc', 0)
        art = mp.get('art', 'some')

        # cloth/leather armor: use material as adjective ("a silk gown")
        if mat_type == 'cloth':
            nm = f"{art} {mat} {disp_name}"
            sn = f"{mat} {disp_name}"
        elif mat_type == 'leather_armor':
            nm = f"some {mat} {disp_name}" if mat != 'leather' else f"some {disp_name}"
            sn = f"{mat} {disp_name}"
            art = 'some'
        else:
            nm = f"{art} {mat} {disp_name}"
            sn = f"{mat} {disp_name}"

        add(
            name          = nm,
            short_name    = sn,
            base_name     = disp_name,
            noun          = noun,
            article       = art,
            item_type     = 'armor',
            material      = mat,
            armor_asg     = asg,
            armor_group   = asg,
            cva           = cva,
            action_penalty = act_pen,
            spell_hindrance = sp_hind,
            enchant_bonus = enc,
            defense_bonus = 0,
            weight        = wt,
            value         = val,
            is_template   = 1,
            description   = f"A {mat} {disp_name} (ASG {asg}).",
        )

# ----- SHIELDS --------------------------------------------------------------

SHIELD_METALS = {k: v for k, v in METALS.items()
                 if v['avail'] <= 3}  # leave out ultra-rare metals for shields

for (base_name, noun, size, base_ds, evade_pen, base_wt, base_val, _) in SHIELD_FORMS:
    for mat, mp in SHIELD_METALS.items():
        wt  = round2(base_wt * mp['wt'])
        val = max(1, int(base_val * mp['val']))
        enc = mp['enc']
        art = mp['art']
        nm  = f"{art} {mat} {base_name}"
        sn  = f"{mat} {base_name}"
        add(
            name          = nm,
            short_name    = sn,
            base_name     = base_name,
            noun          = noun,
            article       = art,
            item_type     = 'shield',
            material      = mat,
            shield_size   = size,
            shield_ds     = base_ds,
            shield_evade_penalty = evade_pen,
            enchant_bonus = enc,
            weight        = wt,
            value         = val,
            is_template   = 1,
            description   = f"A {mat} {base_name}.",
        )

# ----- GEMS -----------------------------------------------------------------

for (nm, noun, family, val) in GEMS:
    art = nm.split()[0]
    add(name=nm, short_name=nm.lstrip('a ').lstrip('an ').lstrip('some '),
        base_name=noun, noun=noun, article=art,
        item_type='gem', gem_family=family,
        weight=1.0, value=val, is_stackable=1, is_template=1,
        description=nm)

# ----- HERBS ----------------------------------------------------------------

for (nm, noun, htype, hamount, val) in HERBS:
    art = nm.split()[0]
    add(name=nm, short_name=nm.lstrip('a ').lstrip('an ').lstrip('some '),
        base_name=noun, noun=noun, article=art,
        item_type='herb', herb_heal_type=htype, herb_heal_amount=hamount,
        weight=1.0, value=val, is_stackable=1, is_template=1,
        description=nm)

# ----- LOCKPICKS ------------------------------------------------------------

for (nm, noun, mat, modifier, val) in LOCKPICKS:
    art = nm.split()[0]
    add(name=nm, short_name=nm.lstrip('a ').lstrip('an '),
        base_name='lockpick', noun=noun, article=art,
        item_type='misc', material=mat, lockpick_modifier=modifier,
        weight=1.0, value=val, is_template=1,
        description=nm)

# ----- CREATURE DROPS -------------------------------------------------------

for (nm, noun, itype, val, source) in CREATURE_DROPS:
    art = nm.split()[0]
    add(name=nm, short_name=nm.lstrip('a ').lstrip('an ').lstrip('some '),
        base_name=noun, noun=noun, article=art,
        item_type=itype, creature_source=source,
        weight=1.0, value=val, is_template=1,
        description=nm)

# ----- CONTAINERS -----------------------------------------------------------

for (nm, sn, noun, cap, wt, val) in CONTAINERS:
    art = nm.split()[0]
    add(name=nm, short_name=sn, base_name=noun, noun=noun, article=art,
        item_type='container', container_capacity=cap,
        weight=wt, value=val, is_template=1,
        description=nm)

# ----- CLOTHING -------------------------------------------------------------

for (noun, worn_loc, base_wt, base_val) in CLOTHING_BASES:
    for color in CLOTH_COLORS:
        for cloth, cp in CLOTHS.items():
            art = 'an' if color[0] in 'aeiou' else 'a'
            nm  = f"{art} {color} {cloth} {noun}"
            sn  = f"{color} {cloth} {noun}"
            wt  = round2(base_wt * cp['wt'])
            val = max(1, int(base_val * cp['val']))
            add(name=nm, short_name=sn, base_name=noun, noun=noun, article=art,
                item_type='misc', material=cloth, worn_location=worn_loc,
                weight=wt, value=val, is_template=1,
                description=f"A {color} {cloth} {noun}.")

# ----- FOOD & DRINK ---------------------------------------------------------

for (nm, noun, itype, val, stackable) in FOOD_ITEMS:
    art = nm.split()[0]
    add(name=nm, short_name=nm.lstrip('a ').lstrip('an ').lstrip('some '),
        base_name=noun, noun=noun, article=art,
        item_type=itype, weight=1.0, value=val,
        is_stackable=stackable, is_template=1,
        description=nm)

# ----- MISC -----------------------------------------------------------------

for (nm, noun, itype, wt, val) in MISC_ITEMS:
    art = nm.split()[0]
    add(name=nm, short_name=nm.lstrip('a ').lstrip('an ').lstrip('some '),
        base_name=noun, noun=noun, article=art,
        item_type=itype, weight=wt, value=val, is_template=1,
        description=nm)

# ---------------------------------------------------------------------------
# OUTPUT SQL
# ---------------------------------------------------------------------------

ALL_COLS = [
    'name','short_name','base_name','noun','article','item_type','material',
    'weapon_type','weapon_category','damage_factor','damage_type',
    'weapon_speed','attack_bonus','damage_bonus',
    'armor_asg','armor_group','cva','defense_bonus','action_penalty','spell_hindrance',
    'shield_size','shield_ds','shield_evade_penalty',
    'container_capacity','enchant_bonus','gem_family',
    'herb_heal_type','herb_heal_amount','lockpick_modifier',
    'creature_source','worn_location',
    'weight','value','is_stackable','is_template','description',
]

BATCH = 200  # rows per INSERT statement

print("-- =============================================================")
print("-- Ta'Vaalor Generated Item Catalog")
print(f"-- {len(rows):,} items total")
print("-- Generated by database/generators/generate_items.py")
print("-- =============================================================")
print("USE gemstone_dev;")
print()

def row_to_sql(r):
    parts = []
    for col in ALL_COLS:
        v = r.get(col)
        if v is None:
            parts.append('NULL')
        elif isinstance(v, bool):
            parts.append('1' if v else '0')
        elif isinstance(v, int):
            parts.append(str(v))
        elif isinstance(v, float):
            parts.append(str(v))
        elif isinstance(v, str):
            parts.append(esc(v))
        else:
            parts.append(esc(str(v)))
    return "(" + ",".join(parts) + ")"

col_list = ",".join(ALL_COLS)

for i in range(0, len(rows), BATCH):
    chunk = rows[i:i+BATCH]
    vals  = ",\n  ".join(row_to_sql(r) for r in chunk)
    print(f"INSERT IGNORE INTO items ({col_list}) VALUES")
    print(f"  {vals};")
    print()

print(f"-- Done. Total items: {len(rows):,}")
print("SELECT item_type, COUNT(*) as count FROM items GROUP BY item_type ORDER BY item_type;")
print("SELECT CONCAT('Total items: ', COUNT(*)) FROM items;")

sys.stderr.write(f"Generated {len(rows):,} items\n")
