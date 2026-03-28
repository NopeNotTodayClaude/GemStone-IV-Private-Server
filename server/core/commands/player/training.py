"""
training.py  -  GemStone IV TRAIN verb and skill cost system.

GS4 Canon:
  - TRAIN <skill> [<ranks>]  -- spend TPs to gain ranks
  - TRAIN LIST               -- show all trainable skills with costs
  - Costs vary by profession (squares pay less for combat, pures for magic)
  - Costs DOUBLE for the 2nd purchase within a "level slot"
  - Max TOTAL ranks = train_limit_per_level × character_level
    e.g. TWC with limit 2, level 5 Warrior => max 10 ranks total.
    A level 5 can dump all 10 at once if they have 0 and the TPs.
    There is NO per-session purchase restriction — only a total rank ceiling.

Cost-doubling formula (canonical GS4):
  Within each group of <limit> ranks, the Nth purchase costs N× base.
  slot_position(rank, limit) = ((rank - 1) % limit) + 1
  cost_for_rank(rank) = base × slot_position(rank, limit)
  Example: TWC limit=2, base=2/2
    Rank 1: slot_pos=1, cost 2/2
    Rank 2: slot_pos=2, cost 4/4
    Rank 3: slot_pos=1, cost 2/2  (new level-slot)
    Rank 4: slot_pos=2, cost 4/4

Bonus formula (GS4 wiki canonical):
  Ranks  1-10: +5 per rank  (max at rank 10: +50)
  Ranks 11-20: +4 per rank  (max at rank 20: +90)
  Ranks 21-30: +3 per rank  (max at rank 30: +120)
  Ranks 31-40: +2 per rank  (max at rank 40: +140)
  Ranks   41+: +1 per rank  (formula: rank + 100)
"""

import logging
from server.core.protocol.colors import colorize, TextPresets
from server.core.commands.player.weapon_techniques import check_technique_grants

log = logging.getLogger(__name__)

# ── Skill ID -> Display Name ──────────────────────────────────────────────────
SKILL_NAMES = {
    1:  "Two Weapon Combat",
    2:  "Armor Use",
    3:  "Shield Use",
    4:  "Combat Maneuvers",
    5:  "Edged Weapons",
    6:  "Blunt Weapons",
    7:  "Two-Handed Weapons",
    8:  "Ranged Weapons",
    9:  "Thrown Weapons",
    10: "Polearm Weapons",
    11: "Brawling",
    12: "Multi Opponent Combat",
    13: "Physical Fitness",
    14: "Dodging",
    15: "Arcane Symbols",
    16: "Magic Item Use",
    17: "Spell Aiming",
    18: "Harness Power",
    19: "Elemental Mana Control",
    20: "Spirit Mana Control",
    21: "Mental Mana Control",
    22: "Spell Research",
    23: "Survival",
    24: "Disarming Traps",
    25: "Picking Locks",
    26: "Stalking and Hiding",
    27: "Perception",
    28: "Climbing",
    29: "Swimming",
    30: "First Aid",
    31: "Trading",
    32: "Pickpocketing",
    33: "Spiritual Lore - Blessings",
    34: "Spiritual Lore - Religion",
    35: "Spiritual Lore - Summoning",
    36: "Elemental Lore - Air",
    37: "Elemental Lore - Earth",
    38: "Elemental Lore - Fire",
    39: "Elemental Lore - Water",
    40: "Mental Lore - Manipulation",
    41: "Mental Lore - Telepathy",
    42: "Mental Lore - Transference",
    43: "Ambush",
    44: "Mental Lore - Divination",
    45: "Mental Lore - Transformation",
    46: "Sorcerous Lore - Demonology",
    47: "Sorcerous Lore - Necromancy",
}

def _norm(s):
    return s.lower().replace(' ', '').replace('-', '').replace("'", '')

SKILL_BY_NAME = {_norm(v): k for k, v in SKILL_NAMES.items()}

SKILL_ALIASES = {
    'twc':          1,  'twoweapon': 1,
    'armor':        2,
    'shield':       3,
    'cm':           4,  'combatman': 4,
    'edged':        5,  'edgedweapons': 5,
    'blunt':        6,  'bluntweapons': 6,
    'twohanded':    7,  '2h': 7,
    'ranged':       8,  'rangedweapons': 8,
    'thrown':       9,  'thrownweapons': 9,
    'polearm':      10, 'polearmweapons': 10,
    'brawling':     11,
    'moc':          12, 'multiopponent': 12,
    'pf':           13, 'physicalfitness': 13,
    'dodging':      14,
    'arcanesymbols':15, 'arcane': 15,
    'miu':          16, 'magicitemuse': 16,
    'spellaiming':  17, 'aiming': 17,
    'harnesspower': 18, 'harness': 18,
    'emc':          19, 'elementalmana': 19,
    'smc':          20, 'spiritualmana': 20, 'spiritmana': 20,
    'mmc':          21, 'mentalmana': 21,
    'spellresearch':22, 'research': 22,
    'survival':     23,
    'disarm':       24, 'disarming': 24, 'disarmingtraps': 24,
    'pickinglocks': 25, 'lockpick': 25, 'locks': 25,
    'stalking':     26, 'hiding': 26, 'stalkingandhi': 26, 'sneak': 26,
    'perception':   27,
    'climbing':     28, 'climb': 28,
    'swimming':     29, 'swim': 29,
    'firstaid':     30, 'aid': 30,
    'trading':      31, 'trade': 31,
    'pickpocketing':32, 'pickpocket': 32,
    'blessings':    33,
    'religion':     34,
    'summoning':    35,
    'airlore':      36,
    'earthlore':    37,
    'firelore':     38,
    'waterlore':    39,
    'manipulation': 40,
    'telepathy':    41,
    'transference': 42,
    'ambush':       43, 'amb': 43,
    'divination':   44,
    'transformation': 45,
    'demonology':   46,
    'necromancy':   47,
}

# ── TP Costs (PTP, MTP) per rank, by profession_id ───────────────────────────
# Source: gswiki.play.net — verified against individual skill pages
# Prof IDs: 1=Warrior 2=Rogue 3=Wizard 4=Cleric 5=Empath
#           6=Sorcerer 7=Ranger 8=Bard 9=Paladin 10=Monk
# (ptp, mtp) per rank.  (0, 0) = profession cannot train this skill.
SKILL_COSTS = {
    #  Skill ID: { prof_id: (ptp, mtp), ... }
    1:  {1:(2,2),  2:(2,2),  3:(12,12),4:(9,9),  5:(12,12),6:(12,12),7:(3,2),  8:(3,2),  9:(3,3),  10:(2,2)},  # TWC
    2:  {1:(2,0),  2:(3,0),  3:(10,0), 4:(6,0),  5:(8,0),  6:(10,0), 7:(4,0),  8:(4,0),  9:(3,0),  10:(5,0)},  # Armor Use
    3:  {1:(2,0),  2:(3,0),  3:(8,0),  4:(4,0),  5:(6,0),  6:(8,0),  7:(4,0),  8:(5,0),  9:(2,0),  10:(6,0)},  # Shield Use
    4:  {1:(2,2),  2:(3,3),  3:(10,10),4:(8,8),  5:(10,10),6:(10,10),7:(4,4),  8:(5,5),  9:(4,4),  10:(3,3)},  # Combat Maneuvers
    5:  {1:(3,0),  2:(4,0),  3:(15,0), 4:(10,0), 5:(15,0), 6:(15,0), 7:(5,0),  8:(5,0),  9:(5,0),  10:(6,0)},  # Edged Weapons
    6:  {1:(3,0),  2:(5,0),  3:(15,0), 4:(8,0),  5:(15,0), 6:(15,0), 7:(5,0),  8:(5,0),  9:(5,0),  10:(6,0)},  # Blunt Weapons
    7:  {1:(3,0),  2:(6,0),  3:(15,0), 4:(10,0), 5:(15,0), 6:(15,0), 7:(5,0),  8:(6,0),  9:(5,0),  10:(5,0)},  # Two-Handed Weapons
    8:  {1:(4,0),  2:(3,0),  3:(15,0), 4:(12,0), 5:(15,0), 6:(15,0), 7:(3,0),  8:(5,0),  9:(6,0),  10:(6,0)},  # Ranged Weapons
    9:  {1:(4,0),  2:(3,0),  3:(15,0), 4:(12,0), 5:(15,0), 6:(15,0), 7:(4,0),  8:(5,0),  9:(6,0),  10:(5,0)},  # Thrown Weapons
    10: {1:(3,0),  2:(6,0),  3:(15,0), 4:(10,0), 5:(15,0), 6:(15,0), 7:(4,0),  8:(6,0),  9:(5,0),  10:(5,0)},  # Polearm Weapons
    11: {1:(3,0),  2:(3,0),  3:(15,0), 4:(10,0), 5:(10,0), 6:(15,0), 7:(5,0),  8:(5,0),  9:(5,0),  10:(2,0)},  # Brawling
    12: {1:(3,3),  2:(5,5),  3:(15,15),4:(10,10),5:(15,15),6:(15,15),7:(5,5),  8:(5,5),  9:(5,5),  10:(4,4)},  # Multi Opponent Combat
    13: {1:(1,0),  2:(2,0),  3:(3,0),  4:(2,0),  5:(2,0),  6:(3,0),  7:(1,0),  8:(2,0),  9:(1,0),  10:(1,0)},  # Physical Fitness
    14: {1:(3,0),  2:(2,0),  3:(6,0),  4:(4,0),  5:(5,0),  6:(6,0),  7:(3,0),  8:(3,0),  9:(4,0),  10:(2,0)},  # Dodging
    15: {1:(0,4),  2:(0,4),  3:(0,1),  4:(0,2),  5:(0,2),  6:(0,1),  7:(0,3),  8:(0,2),  9:(0,3),  10:(0,4)},  # Arcane Symbols
    16: {1:(0,4),  2:(0,3),  3:(0,2),  4:(0,2),  5:(0,2),  6:(0,2),  7:(0,3),  8:(0,2),  9:(0,3),  10:(0,3)},  # Magic Item Use
    17: {1:(4,8),  2:(4,5),  3:(2,1),  4:(3,1),  5:(3,1),  6:(3,1),  7:(4,1),  8:(4,1),  9:(4,2),  10:(3,4)},  # Spell Aiming
    18: {1:(0,10), 2:(0,9),  3:(0,4),  4:(0,4),  5:(0,4),  6:(0,4),  7:(0,5),  8:(0,5),  9:(0,5),  10:(0,6)},  # Harness Power
    19: {1:(0,6),  2:(0,6),  3:(0,2),  4:(0,6),  5:(0,6),  6:(0,3),  7:(0,6),  8:(0,4),  9:(0,6),  10:(0,6)},  # Elemental Mana Control
    20: {1:(0,6),  2:(0,6),  3:(0,6),  4:(0,2),  5:(0,2),  6:(0,3),  7:(0,4),  8:(0,4),  9:(0,4),  10:(0,6)},  # Spirit Mana Control
    21: {1:(0,6),  2:(0,6),  3:(0,6),  4:(0,6),  5:(0,4),  6:(0,6),  7:(0,6),  8:(0,4),  9:(0,6),  10:(0,4)},  # Mental Mana Control
    22: {1:(0,120),2:(0,67), 3:(0,8),  4:(0,8),  5:(0,8),  6:(0,8),  7:(0,17), 8:(0,17), 9:(0,27), 10:(0,38)}, # Spell Research
    23: {1:(2,0),  2:(2,0),  3:(3,0),  4:(3,0),  5:(3,0),  6:(3,0),  7:(1,0),  8:(2,0),  9:(2,0),  10:(2,0)},  # Survival
    24: {1:(0,8),  2:(2,2),  3:(0,8),  4:(0,8),  5:(0,8),  6:(0,8),  7:(0,6),  8:(0,6),  9:(0,8),  10:(0,6)},  # Disarming Traps
    25: {1:(0,8),  2:(2,2),  3:(0,8),  4:(0,8),  5:(0,8),  6:(0,8),  7:(0,6),  8:(0,6),  9:(0,8),  10:(0,6)},  # Picking Locks
    26: {1:(4,0),  2:(2,0),  3:(6,0),  4:(6,0),  5:(6,0),  6:(6,0),  7:(3,0),  8:(3,0),  9:(6,0),  10:(3,0)},  # Stalking and Hiding
    27: {1:(0,3),  2:(0,2),  3:(0,3),  4:(0,2),  5:(0,2),  6:(0,3),  7:(0,2),  8:(0,2),  9:(0,3),  10:(0,2)},  # Perception
    28: {1:(1,0),  2:(1,0),  3:(2,0),  4:(2,0),  5:(2,0),  6:(2,0),  7:(1,0),  8:(1,0),  9:(1,0),  10:(1,0)},  # Climbing
    29: {1:(1,0),  2:(1,0),  3:(2,0),  4:(2,0),  5:(2,0),  6:(2,0),  7:(1,0),  8:(1,0),  9:(1,0),  10:(1,0)},  # Swimming
    30: {1:(0,2),  2:(0,2),  3:(0,3),  4:(0,2),  5:(0,1),  6:(0,3),  7:(0,2),  8:(0,2),  9:(0,2),  10:(0,2)},  # First Aid
    31: {1:(0,3),  2:(0,2),  3:(0,3),  4:(0,3),  5:(0,3),  6:(0,3),  7:(0,3),  8:(0,2),  9:(0,3),  10:(0,3)},  # Trading
    32: {1:(6,0),  2:(2,0),  3:(8,0),  4:(8,0),  5:(8,0),  6:(8,0),  7:(6,0),  8:(4,0),  9:(8,0),  10:(4,0)},  # Pickpocketing
    33: {1:(0,4),  2:(0,4),  3:(0,3),  4:(0,2),  5:(0,3),  6:(0,3),  7:(0,4),  8:(0,3),  9:(0,3),  10:(0,4)},  # Spiritual Lore - Blessings
    34: {1:(0,4),  2:(0,4),  3:(0,3),  4:(0,2),  5:(0,3),  6:(0,3),  7:(0,4),  8:(0,3),  9:(0,3),  10:(0,4)},  # Spiritual Lore - Religion
    35: {1:(0,4),  2:(0,4),  3:(0,3),  4:(0,3),  5:(0,3),  6:(0,2),  7:(0,4),  8:(0,3),  9:(0,4),  10:(0,4)},  # Spiritual Lore - Summoning
    36: {1:(0,4),  2:(0,4),  3:(0,2),  4:(0,4),  5:(0,4),  6:(0,3),  7:(0,4),  8:(0,3),  9:(0,4),  10:(0,4)},  # Elemental Lore - Air
    37: {1:(0,4),  2:(0,4),  3:(0,2),  4:(0,4),  5:(0,4),  6:(0,3),  7:(0,3),  8:(0,3),  9:(0,4),  10:(0,4)},  # Elemental Lore - Earth
    38: {1:(0,4),  2:(0,4),  3:(0,2),  4:(0,4),  5:(0,4),  6:(0,2),  7:(0,4),  8:(0,3),  9:(0,4),  10:(0,4)},  # Elemental Lore - Fire
    39: {1:(0,4),  2:(0,4),  3:(0,2),  4:(0,4),  5:(0,4),  6:(0,3),  7:(0,3),  8:(0,3),  9:(0,4),  10:(0,4)},  # Elemental Lore - Water
    40: {1:(0,40), 2:(0,40), 3:(0,20), 4:(0,20), 5:(0,6),  6:(0,20), 7:(0,20), 8:(0,8),  9:(0,20), 10:(0,12)}, # Mental Lore - Manipulation
    41: {1:(0,40), 2:(0,40), 3:(0,20), 4:(0,20), 5:(0,6),  6:(0,20), 7:(0,20), 8:(0,8),  9:(0,20), 10:(0,12)}, # Mental Lore - Telepathy
    42: {1:(0,40), 2:(0,40), 3:(0,20), 4:(0,20), 5:(0,6),  6:(0,20), 7:(0,20), 8:(0,8),  9:(0,20), 10:(0,12)}, # Mental Lore - Transference
    43: {1:(3,4),  2:(2,1),  3:(15,10),4:(12,12),5:(15,15),6:(15,14),7:(3,3),  8:(4,4),  9:(4,5),  10:(3,2)},  # Ambush
    44: {1:(0,40), 2:(0,40), 3:(0,20), 4:(0,20), 5:(0,6),  6:(0,20), 7:(0,20), 8:(0,8),  9:(0,20), 10:(0,12)}, # Mental Lore - Divination
    45: {1:(0,40), 2:(0,40), 3:(0,20), 4:(0,20), 5:(0,6),  6:(0,20), 7:(0,20), 8:(0,8),  9:(0,20), 10:(0,12)}, # Mental Lore - Transformation
    46: {1:(0,30), 2:(0,30), 3:(0,10), 4:(0,10), 5:(0,12), 6:(0,6),  7:(0,18), 8:(0,18), 9:(0,18), 10:(0,35)}, # Sorcerous Lore - Demonology
    47: {1:(0,30), 2:(0,30), 3:(0,10), 4:(0,10), 5:(0,12), 6:(0,6),  7:(0,18), 8:(0,18), 9:(0,18), 10:(0,35)}, # Sorcerous Lore - Necromancy
}

# ── Max ranks TRAINABLE PER LEVEL by skill + profession ──────────────────────
# Source: gswiki individual skill pages.
# TOTAL rank cap = train_limit × character_level.
# A level 5 Warrior has a TWC cap of 2×5 = 10 ranks.
# A level 2 Warrior has a TWC cap of 2×2 = 4 ranks.
# You may purchase up to that total at any time — no per-session restriction.
# 0 = profession cannot train this skill at all.
SKILL_TRAIN_LIMITS = {
    # skill_id: {prof_id: ranks_per_level, ...}
    1:  {1:2, 2:2, 3:1, 4:1, 5:1, 6:1, 7:2, 8:2, 9:2, 10:2},  # TWC
    2:  {1:3, 2:3, 3:1, 4:2, 5:2, 6:1, 7:2, 8:2, 9:3, 10:3},  # Armor Use
    3:  {1:3, 2:3, 3:1, 4:2, 5:2, 6:1, 7:2, 8:2, 9:3, 10:2},  # Shield Use
    4:  {1:3, 2:3, 3:1, 4:2, 5:2, 6:1, 7:2, 8:2, 9:2, 10:3},  # Combat Maneuvers
    5:  {1:3, 2:3, 3:1, 4:1, 5:1, 6:1, 7:2, 8:2, 9:2, 10:2},  # Edged Weapons
    6:  {1:3, 2:3, 3:1, 4:1, 5:1, 6:1, 7:2, 8:2, 9:2, 10:2},  # Blunt Weapons
    7:  {1:3, 2:2, 3:1, 4:1, 5:1, 6:1, 7:2, 8:2, 9:2, 10:2},  # Two-Handed Weapons
    8:  {1:2, 2:3, 3:1, 4:1, 5:1, 6:1, 7:3, 8:2, 9:2, 10:2},  # Ranged Weapons
    9:  {1:2, 2:3, 3:1, 4:1, 5:1, 6:1, 7:2, 8:2, 9:2, 10:2},  # Thrown Weapons
    10: {1:3, 2:2, 3:1, 4:1, 5:1, 6:1, 7:2, 8:2, 9:2, 10:2},  # Polearm Weapons
    11: {1:3, 2:3, 3:1, 4:1, 5:1, 6:1, 7:2, 8:2, 9:2, 10:3},  # Brawling
    12: {1:2, 2:2, 3:1, 4:1, 5:1, 6:1, 7:2, 8:2, 9:2, 10:2},  # Multi Opponent Combat
    13: {1:3, 2:3, 3:3, 4:3, 5:3, 6:3, 7:3, 8:3, 9:3, 10:3},  # Physical Fitness
    14: {1:3, 2:3, 3:2, 4:2, 5:2, 6:2, 7:3, 8:3, 9:3, 10:3},  # Dodging
    15: {1:1, 2:1, 3:3, 4:2, 5:2, 6:2, 7:1, 8:2, 9:1, 10:1},  # Arcane Symbols
    16: {1:1, 2:1, 3:3, 4:2, 5:2, 6:2, 7:1, 8:2, 9:1, 10:1},  # Magic Item Use
    17: {1:1, 2:1, 3:2, 4:2, 5:2, 6:2, 7:2, 8:2, 9:2, 10:0},  # Spell Aiming
    18: {1:1, 2:1, 3:3, 4:3, 5:3, 6:3, 7:2, 8:2, 9:2, 10:1},  # Harness Power
    19: {1:1, 2:1, 3:3, 4:1, 5:1, 6:2, 7:1, 8:2, 9:1, 10:1},  # Elemental Mana Control
    20: {1:1, 2:1, 3:1, 4:3, 5:3, 6:2, 7:2, 8:2, 9:2, 10:1},  # Spirit Mana Control
    21: {1:1, 2:1, 3:1, 4:1, 5:2, 6:1, 7:1, 8:2, 9:1, 10:3},  # Mental Mana Control
    22: {1:1, 2:1, 3:3, 4:3, 5:3, 6:3, 7:2, 8:2, 9:2, 10:1},  # Spell Research
    23: {1:2, 2:2, 3:2, 4:2, 5:2, 6:2, 7:3, 8:2, 9:2, 10:2},  # Survival
    24: {1:1, 2:3, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1, 9:1, 10:1},  # Disarming Traps
    25: {1:1, 2:3, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1, 9:1, 10:1},  # Picking Locks
    26: {1:2, 2:3, 3:1, 4:1, 5:1, 6:1, 7:2, 8:2, 9:1, 10:2},  # Stalking and Hiding
    27: {1:2, 2:2, 3:2, 4:2, 5:2, 6:2, 7:2, 8:2, 9:2, 10:2},  # Perception
    28: {1:3, 2:3, 3:2, 4:2, 5:2, 6:2, 7:3, 8:3, 9:3, 10:3},  # Climbing
    29: {1:3, 2:3, 3:2, 4:2, 5:2, 6:2, 7:3, 8:3, 9:3, 10:3},  # Swimming
    30: {1:2, 2:2, 3:2, 4:2, 5:3, 6:2, 7:2, 8:2, 9:2, 10:2},  # First Aid
    31: {1:2, 2:2, 3:2, 4:2, 5:2, 6:2, 7:2, 8:2, 9:2, 10:2},  # Trading
    32: {1:1, 2:3, 3:1, 4:1, 5:1, 6:1, 7:1, 8:2, 9:1, 10:1},  # Pickpocketing
    33: {1:1, 2:1, 3:1, 4:2, 5:2, 6:1, 7:1, 8:1, 9:2, 10:1},
    34: {1:1, 2:1, 3:1, 4:2, 5:2, 6:1, 7:1, 8:1, 9:2, 10:1},
    35: {1:1, 2:1, 3:1, 4:2, 5:2, 6:2, 7:1, 8:1, 9:1, 10:1},
    36: {1:1, 2:1, 3:2, 4:1, 5:1, 6:2, 7:1, 8:2, 9:1, 10:1},
    37: {1:1, 2:1, 3:2, 4:1, 5:1, 6:2, 7:1, 8:1, 9:1, 10:1},
    38: {1:1, 2:1, 3:2, 4:1, 5:1, 6:2, 7:1, 8:1, 9:1, 10:1},
    39: {1:1, 2:1, 3:2, 4:1, 5:1, 6:2, 7:1, 8:2, 9:1, 10:1},
    40: {1:1, 2:1, 3:1, 4:1, 5:2, 6:1, 7:1, 8:2, 9:1, 10:1},
    41: {1:1, 2:1, 3:1, 4:1, 5:2, 6:1, 7:1, 8:2, 9:1, 10:1},
    42: {1:1, 2:1, 3:1, 4:1, 5:2, 6:1, 7:1, 8:2, 9:1, 10:1},
    43: {1:2, 2:2, 3:1, 4:1, 5:1, 6:1, 7:2, 8:1, 9:1, 10:2},
    44: {1:1, 2:1, 3:1, 4:1, 5:2, 6:1, 7:1, 8:2, 9:1, 10:1},
    45: {1:1, 2:1, 3:1, 4:1, 5:2, 6:1, 7:1, 8:2, 9:1, 10:1},
    46: {1:1, 2:1, 3:1, 4:1, 5:1, 6:2, 7:1, 8:1, 9:1, 10:1},
    47: {1:1, 2:1, 3:1, 4:1, 5:1, 6:2, 7:1, 8:1, 9:1, 10:1},
}

# ── Skill categories for LIST display ────────────────────────────────────────
SKILL_CATEGORIES = {
    "Combat":   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 43],
    "Magic":    [15, 16, 17, 18, 19, 20, 21, 22],
    "Survival": [23, 24, 25, 26, 27, 28, 29],
    "General":  [30, 31, 32],
    "Lore":     [33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47],
}

_LUA_SKILLS_LOADED = False


def _try_load_lua_skills(server=None):
    """Refresh exported skill tables from Lua once the runtime is available."""
    global _LUA_SKILLS_LOADED
    if _LUA_SKILLS_LOADED or server is None:
        return

    try:
        lua = getattr(server, "lua", None)
        if lua is None:
            return
        skills_data = lua.get_skills()
        if not skills_data:
            return

        global SKILL_NAMES, SKILL_BY_NAME, SKILL_ALIASES
        global SKILL_COSTS, SKILL_TRAIN_LIMITS, SKILL_CATEGORIES

        if skills_data.get("skill_names"):
            SKILL_NAMES = skills_data["skill_names"]
            SKILL_BY_NAME = {_norm(v): k for k, v in SKILL_NAMES.items()}
        if skills_data.get("skill_aliases"):
            SKILL_ALIASES = dict(skills_data["skill_aliases"])
        if skills_data.get("skill_costs"):
            SKILL_COSTS = skills_data["skill_costs"]
        if skills_data.get("train_limits"):
            SKILL_TRAIN_LIMITS = skills_data["train_limits"]
        if skills_data.get("categories"):
            SKILL_CATEGORIES = skills_data["categories"]

        _LUA_SKILLS_LOADED = True
        log.info("training: skill data loaded from Lua")
    except Exception as e:
        log.warning("training: Lua skill load skipped: %s", e)


# ── Core helpers ──────────────────────────────────────────────────────────────

def calc_skill_bonus(ranks: int) -> int:
    """
    GS4 canonical skill bonus formula (source: gswiki.play.net/Skill).
      Ranks  1-10: +5 per rank  (max 50)
      Ranks 11-20: +4 per rank  (max 90)
      Ranks 21-30: +3 per rank  (max 120)
      Ranks 31-40: +2 per rank  (max 140)
      Ranks   41+: +1 per rank  (= ranks + 100)
    """
    if ranks <= 0:  return 0
    if ranks <= 10: return ranks * 5
    if ranks <= 20: return 50 + (ranks - 10) * 4
    if ranks <= 30: return 90 + (ranks - 20) * 3
    if ranks <= 40: return 120 + (ranks - 30) * 2
    return ranks + 100


def get_skill_cost(skill_id: int, prof_id: int):
    """Return (ptp_cost, mtp_cost) base cost per rank for this skill/profession."""
    return SKILL_COSTS.get(skill_id, {}).get(prof_id, (0, 0))


def get_train_limit(skill_id: int, prof_id: int) -> int:
    """Return max ranks per level for this skill/profession. 0 = cannot train."""
    return SKILL_TRAIN_LIMITS.get(skill_id, {}).get(prof_id, 1)


def get_max_ranks(skill_id: int, prof_id: int, level: int) -> int:
    """
    Return the TOTAL rank ceiling for a skill at the given character level.
    Formula: train_limit_per_level × level.
    Example: TWC limit=2, level=5  =>  max 10 ranks.
    """
    limit = get_train_limit(skill_id, prof_id)
    if limit == 0:
        return 0
    return limit * level


def cost_for_rank_range(ptp_base: int, mtp_base: int, limit: int,
                        level: int, from_rank: int, to_rank: int):
    """
    Calculate total (ptp, mtp) cost to buy ranks from_rank+1 through to_rank.

    GS4 canon cost model (level-aware):
      prev_cap = limit x (level - 1)
        Ranks 1..prev_cap  are prior-level ranks  -> flat base cost (slot_pos=1).
        Ranks prev_cap+1.. are current-level slots -> slot_pos capped at 2.
          Slot 1: 1x base (no premium)
          Slot 2+: 2x base (doubled, never tripled regardless of limit)

    At level 20 TWC limit=2: ranks 1-38 flat 2/2. Rank 39: 2/2. Rank 40: 4/4.
    At level 2 Blunt limit=3: ranks 1-3 flat, rank 4: 3, rank 5: 6, rank 6: 6.
    On level-up premiums are refunded (see experience_manager._level_up).
    """
    if limit <= 0:
        limit = 1
    prev_cap  = limit * (level - 1)
    total_ptp = 0
    total_mtp = 0
    for rank in range(from_rank + 1, to_rank + 1):
        if rank <= prev_cap:
            slot_pos = 1
        else:
            slot_pos = min(rank - prev_cap, 2)  # never exceeds 2x — no tripling
        total_ptp += ptp_base * slot_pos
        total_mtp += mtp_base * slot_pos
    return total_ptp, total_mtp


def get_next_rank_cost(skill_id: int, prof_id: int, current_ranks: int, level: int):
    """
    Return (ptp, mtp) cost for the next single rank of this skill at this level.
    Only current-level slots carry the doubling premium.
    """
    ptp_base, mtp_base = get_skill_cost(skill_id, prof_id)
    if ptp_base == 0 and mtp_base == 0:
        return (0, 0)
    limit     = get_train_limit(skill_id, prof_id) or 1
    prev_cap  = limit * (level - 1)
    next_rank = current_ranks + 1
    if next_rank <= prev_cap:
        slot_pos = 1
    else:
        slot_pos = min(next_rank - prev_cap, 2)  # never exceeds 2x
    return (ptp_base * slot_pos, mtp_base * slot_pos)


def get_effective_cost(skill_id: int, prof_id: int, current_ranks: int, level: int = 1):
    return get_next_rank_cost(skill_id, prof_id, current_ranks, level)

get_max_per_level = get_train_limit


def resolve_skill(arg: str):
    """
    Resolve a player's skill argument to a skill_id.
    Returns (skill_id, skill_name) or (None, None).
    """
    arg = arg.strip().lower()
    key = arg.replace(' ', '').replace('-', '').replace("'", '')

    if key in SKILL_ALIASES:
        sid = SKILL_ALIASES[key]
        return sid, SKILL_NAMES[sid]

    if key in SKILL_BY_NAME:
        sid = SKILL_BY_NAME[key]
        return sid, SKILL_NAMES[sid]

    matches = [(sid, name) for sid, name in SKILL_NAMES.items()
               if key in _norm(name)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        matches.sort(key=lambda x: len(x[1]))
        return matches[0]

    return None, None


# ── TRAIN command ─────────────────────────────────────────────────────────────

async def cmd_train(session, cmd, args, server):
    """
    TRAIN            - Open the Training Hall web portal.
    TRAIN <skill> [<n>]  - Spend TPs to gain ranks (command-line version).
    TRAIN LIST           - Show all skills with costs.
    """
    _try_load_lua_skills(server)

    if not args:
        if not hasattr(server, 'training_web') or not server.training_web:
            await session.send_line(colorize(
                "The Training Hall web portal is not running.",
                TextPresets.WARNING
            ))
            return

        token = server.training_web.generate_token(session)
        url   = f"http://{session.server_ip}:8765/train?token={token}"

        await session.send_line(colorize(
            "  The Training Hall has been opened in your browser.",
            TextPresets.EXPERIENCE
        ))
        await session.send_line(colorize(f"  {url}", TextPresets.SYSTEM))
        await session.send_line(colorize(
            "  Changes saved there will be applied immediately.",
            TextPresets.SYSTEM
        ))
        return

    arg = args.strip()

    if arg.lower() in ('list', 'all', 'costs'):
        await _show_skill_list(session)
        return

    # Parse "TRAIN <skill> [<n>]"
    parts = arg.rsplit(None, 1)
    rank_count = 1
    skill_arg  = arg
    if len(parts) == 2 and parts[1].isdigit():
        rank_count = max(1, min(int(parts[1]), 9999))
        skill_arg  = parts[0]

    skill_id, skill_name = resolve_skill(skill_arg)
    if skill_id is None:
        await session.send_line(
            f"I don't recognize the skill '{skill_arg}'.  Try TRAIN LIST."
        )
        return

    prof_id   = getattr(session, 'profession_id', 1)
    level     = getattr(session, 'level', 1)
    ptp_base, mtp_base = get_skill_cost(skill_id, prof_id)

    if ptp_base == 0 and mtp_base == 0:
        await session.send_line(colorize(
            f"Your profession cannot train in {skill_name}.",
            TextPresets.WARNING
        ))
        return

    # ── Total rank cap check ──────────────────────────────────────────────────
    # max_ranks = train_limit_per_level × character_level
    # A level 5 warrior can hold up to 10 TWC ranks total.
    # You can purchase all remaining ranks at once.
    limit     = get_train_limit(skill_id, prof_id)
    max_ranks = get_max_ranks(skill_id, prof_id, level)

    skills    = session.skills or {}
    current   = skills.get(skill_id, {})
    old_ranks = int(current.get('ranks', 0)) if isinstance(current, dict) else 0

    if old_ranks >= max_ranks:
        await session.send_line(colorize(
            f"  You have reached the maximum {max_ranks} ranks in {skill_name} "
            f"for your level ({limit}/level × level {level}).  "
            f"You may train more after gaining a level.",
            TextPresets.WARNING
        ))
        return

    available = max_ranks - old_ranks
    if rank_count > available:
        await session.send_line(colorize(
            f"  You can only gain {available} more rank(s) in {skill_name} "
            f"at your current level (cap: {max_ranks}).  "
            f"Training {available} rank(s) instead.",
            TextPresets.WARNING
        ))
        rank_count = available

    # ── Calculate total cost using slot-position doubling ────────────────────
    total_ptp, total_mtp = cost_for_rank_range(
        ptp_base, mtp_base, limit, level, old_ranks, old_ranks + rank_count
    )

    # ── Check TPs ────────────────────────────────────────────────────────────
    if session.physical_tp < total_ptp:
        await session.send_line(colorize(
            f"  You need {total_ptp} physical TPs for {rank_count} rank(s) of "
            f"{skill_name}.  You only have {session.physical_tp}.",
            TextPresets.WARNING
        ))
        return
    if session.mental_tp < total_mtp:
        await session.send_line(colorize(
            f"  You need {total_mtp} mental TPs for {rank_count} rank(s) of "
            f"{skill_name}.  You only have {session.mental_tp}.",
            TextPresets.WARNING
        ))
        return

    # ── Apply ─────────────────────────────────────────────────────────────────
    new_ranks = old_ranks + rank_count
    new_bonus = calc_skill_bonus(new_ranks)

    session.skills[skill_id] = {
        'ranks': new_ranks,
        'bonus': new_bonus,
    }
    session.physical_tp -= total_ptp
    session.mental_tp   -= total_mtp

    if server.db and session.character_id:
        server.db.save_character_skill(
            session.character_id, skill_id, new_ranks, new_bonus
        )
        server.db.save_character_tps(
            session.character_id, session.physical_tp, session.mental_tp
        )

    rank_word  = "rank" if rank_count == 1 else "ranks"
    remaining  = max_ranks - new_ranks
    limit_note = (f"  ({remaining} more rank(s) available up to level cap of {max_ranks})"
                  if remaining > 0 else f"  (Skill cap reached for level {level})")

    await session.send_line(colorize(
        f"  You spend {total_ptp} PTP and {total_mtp} MTP to train "
        f"{rank_count} {rank_word} in {skill_name}.",
        TextPresets.EXPERIENCE
    ))
    await session.send_line(colorize(
        f"  {skill_name}: {old_ranks} -> {new_ranks} ranks  (Bonus: +{new_bonus})",
        TextPresets.EXPERIENCE
    ))
    await session.send_line(colorize(
        f"  Remaining TPs: {session.physical_tp} physical, {session.mental_tp} mental",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(limit_note, TextPresets.SYSTEM))

    # ── Weapon Technique auto-grant ───────────────────────────────────────────
    await check_technique_grants(session, skill_id, new_ranks, server)


async def _show_skill_list(session):
    """Display all trainable skills with costs for this profession."""
    prof_id = getattr(session, 'profession_id', 1)
    level   = getattr(session, 'level', 1)
    skills  = session.skills or {}

    await session.send_line('')
    await session.send_line(colorize(
        f"  Training Costs for {session.character_name} (Level {level})",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(
        f"  PTPs: {session.physical_tp}   MTPs: {session.mental_tp}",
        TextPresets.SYSTEM
    ))
    await session.send_line('')
    await session.send_line(colorize(
        f"  {'Skill':<30} {'Rnk':>4}  {'Bon':>5}  {'Next PTP':>8}  {'Next MTP':>8}  {'Cap':>4}",
        TextPresets.SYSTEM
    ))
    await session.send_line('  ' + '-' * 66)

    for category, skill_ids in SKILL_CATEGORIES.items():
        await session.send_line(colorize(f"  -- {category} --", TextPresets.WARNING))
        for sid in skill_ids:
            name         = SKILL_NAMES[sid]
            ptp_b, mtp_b = get_skill_cost(sid, prof_id)
            limit        = get_train_limit(sid, prof_id)
            max_r        = get_max_ranks(sid, prof_id, level)

            if ptp_b == 0 and mtp_b == 0:
                cost_str = colorize(f"{'--':>8}  {'--':>8}", TextPresets.COMBAT_MISS)
                cap_str  = "  --"
            else:
                current  = skills.get(sid, {})
                cur_ranks = int(current.get('ranks', 0)) if isinstance(current, dict) else 0
                np, nm   = get_next_rank_cost(sid, prof_id, cur_ranks, level)
                cost_str = f"{np:>8}  {nm:>8}"
                cap_str  = f"{max_r:>4}"

            current   = skills.get(sid, {})
            if isinstance(current, dict):
                ranks = int(current.get('ranks', 0))
                bonus = int(current.get('bonus', 0))
            else:
                ranks, bonus = 0, 0

            await session.send_line(
                f"  {name:<30} {ranks:>4}  {bonus:>5}  {cost_str}  {cap_str}"
            )

    await session.send_line('')
    await session.send_line(colorize(
        "  'Next PTP/MTP' is the cost for your next rank (doubles within each level-slot).",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(
        "  'Cap' is your total rank ceiling at your current level.",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(
        "  Use TRAIN <skill> [ranks] to spend training points.",
        TextPresets.SYSTEM
    ))
    await session.send_line('')
