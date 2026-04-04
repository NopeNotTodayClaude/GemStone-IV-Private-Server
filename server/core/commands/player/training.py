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

SPELL_RESEARCH_SKILL_ID = 22
SPELL_CIRCLE_SKILL_BASE = 10000

_LUA_SKILLS_LOADED = False


def spell_circle_subject_id(circle_id: int) -> int:
    return SPELL_CIRCLE_SKILL_BASE + int(circle_id)


def is_spell_circle_subject(skill_id: int) -> bool:
    try:
        value = int(skill_id)
    except Exception:
        return False
    return value >= SPELL_CIRCLE_SKILL_BASE and value < SPELL_CIRCLE_SKILL_BASE + 1000


def spell_circle_id_for_subject(skill_id: int):
    if not is_spell_circle_subject(skill_id):
        return None
    return int(skill_id) - SPELL_CIRCLE_SKILL_BASE


def _spell_circle_data(server=None):
    lua = getattr(server, "lua", None) if server else None
    if not lua:
        return {"circles": {}, "profession_circles": {}}
    try:
        data = lua.get_spell_circles() or {}
        circles = {
            int(circle_id): dict(raw or {})
            for circle_id, raw in dict(data.get("circles") or {}).items()
        }
        profession_circles = {
            int(prof_id): [int(circle_id) for circle_id in (raw_list or [])]
            for prof_id, raw_list in dict(data.get("profession_circles") or {}).items()
        }
        return {
            "circles": circles,
            "profession_circles": profession_circles,
        }
    except Exception as e:
        log.warning("training: spell circle data load skipped: %s", e)
        return {"circles": {}, "profession_circles": {}}


def get_trainable_spell_circles(prof_id: int, server=None):
    data = _spell_circle_data(server)
    circles = data.get("circles") or {}
    allowed = data.get("profession_circles") or {}
    result = []
    for circle_id in allowed.get(int(prof_id), []):
        row = dict(circles.get(int(circle_id)) or {})
        if not row or not bool(row.get("is_trainable", False)):
            continue
        row["id"] = int(circle_id)
        result.append(row)
    return result


def get_total_spell_ranks(session, server=None, prof_id=None) -> int:
    prof = int(prof_id or getattr(session, "profession_id", 0) or 0)
    allowed_ids = {int(row["id"]) for row in get_trainable_spell_circles(prof, server)}
    ranks_by_circle = dict(getattr(session, "spell_ranks", {}) or {})
    total = 0
    for circle_id, ranks in ranks_by_circle.items():
        try:
            cid = int(circle_id)
            rank_count = max(0, int(ranks or 0))
        except Exception:
            continue
        if allowed_ids and cid not in allowed_ids:
            continue
        total += rank_count
    return total


def get_spell_rank_cap(prof_id: int, level: int) -> int:
    return get_max_ranks(SPELL_RESEARCH_SKILL_ID, prof_id, level)


def get_spell_circle_max_ranks(circle_id: int, session, server=None) -> int:
    prof_id = int(getattr(session, "profession_id", 0) or 0)
    level = int(getattr(session, "level", 1) or 1)
    total_cap = get_spell_rank_cap(prof_id, level)
    current_circle = int((dict(getattr(session, "spell_ranks", {}) or {})).get(int(circle_id), 0) or 0)
    other_ranks = max(0, get_total_spell_ranks(session, server, prof_id) - current_circle)
    return max(0, total_cap - other_ranks)


def get_spell_circle_next_rank_cost(session, server=None):
    prof_id = int(getattr(session, "profession_id", 0) or 0)
    level = int(getattr(session, "level", 1) or 1)
    total_ranks = get_total_spell_ranks(session, server, prof_id)
    return get_next_rank_cost(SPELL_RESEARCH_SKILL_ID, prof_id, total_ranks, level)


def _spell_circle_aliases(circle_row: dict):
    aliases = set()
    name = str(circle_row.get("name") or "").strip()
    abbrev = str(circle_row.get("abbrev") or "").strip()
    if name:
        aliases.add(_norm(name))
        aliases.add(_norm(name.replace(" Base", "")))
    if abbrev:
        aliases.add(_norm(abbrev))
    return aliases


def build_training_catalog(session, server=None):
    prof_id = int(getattr(session, "profession_id", 1) or 1)
    level = int(getattr(session, "level", 1) or 1)
    raw_skills = dict(getattr(session, "skills", {}) or {})
    skills_out = {}

    display_categories = {}
    for category, skill_ids in (SKILL_CATEGORIES or {}).items():
        ids = [int(skill_id) for skill_id in (skill_ids or []) if int(skill_id) != SPELL_RESEARCH_SKILL_ID]
        display_categories[str(category)] = ids

    for skill_id, name in SKILL_NAMES.items():
        if int(skill_id) == SPELL_RESEARCH_SKILL_ID:
            continue
        raw = raw_skills.get(skill_id, {})
        ranks = int(raw.get("ranks", 0)) if isinstance(raw, dict) else 0
        bonus = int(raw.get("bonus", 0)) if isinstance(raw, dict) else 0
        ptp, mtp = get_skill_cost(skill_id, prof_id)
        max_ranks = get_max_ranks(skill_id, prof_id, level)
        limit = get_train_limit(skill_id, prof_id)
        skills_out[int(skill_id)] = {
            "name": str(name),
            "ranks": ranks,
            "bonus": bonus,
            "ptp": ptp,
            "mtp": mtp,
            "base_ptp": ptp,
            "base_mtp": mtp,
            "trainable": not (ptp == 0 and mtp == 0),
            "max_ranks": max_ranks,
            "limit": limit,
            "show_bonus": True,
            "is_spell_circle": False,
        }

    circle_ids = []
    circle_cost_ptp, circle_cost_mtp = get_skill_cost(SPELL_RESEARCH_SKILL_ID, prof_id)
    circle_limit = get_train_limit(SPELL_RESEARCH_SKILL_ID, prof_id)
    next_circle_ptp, next_circle_mtp = get_spell_circle_next_rank_cost(session, server)
    ranks_by_circle = dict(getattr(session, "spell_ranks", {}) or {})
    for circle_row in get_trainable_spell_circles(prof_id, server):
        circle_id = int(circle_row["id"])
        subject_id = spell_circle_subject_id(circle_id)
        current_ranks = int(ranks_by_circle.get(circle_id, 0) or 0)
        max_ranks = get_spell_circle_max_ranks(circle_id, session, server)
        trainable = not (circle_cost_ptp == 0 and circle_cost_mtp == 0)
        at_cap = current_ranks >= max_ranks
        skills_out[subject_id] = {
            "name": str(circle_row.get("name") or f"Circle {circle_id}"),
            "ranks": current_ranks,
            "bonus": 0,
            "ptp": 0 if at_cap else next_circle_ptp,
            "mtp": 0 if at_cap else next_circle_mtp,
            "base_ptp": circle_cost_ptp,
            "base_mtp": circle_cost_mtp,
            "trainable": trainable,
            "max_ranks": max_ranks,
            "limit": circle_limit,
            "show_bonus": False,
            "is_spell_circle": True,
            "circle_id": circle_id,
            "abbrev": str(circle_row.get("abbrev") or ""),
        }
        circle_ids.append(subject_id)

    display_categories["Magic"] = list(display_categories.get("Magic") or []) + circle_ids
    return skills_out, display_categories


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
    if is_spell_circle_subject(skill_id):
        return get_skill_cost(SPELL_RESEARCH_SKILL_ID, prof_id)
    return SKILL_COSTS.get(skill_id, {}).get(prof_id, (0, 0))


def get_train_limit(skill_id: int, prof_id: int) -> int:
    """Return max ranks per level for this skill/profession. 0 = cannot train."""
    if is_spell_circle_subject(skill_id):
        return get_train_limit(SPELL_RESEARCH_SKILL_ID, prof_id)
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


def resolve_skill(arg: str, session=None, server=None):
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

    if session is not None:
        spell_circle_matches = []
        for circle_row in get_trainable_spell_circles(getattr(session, "profession_id", 0), server):
            aliases = _spell_circle_aliases(circle_row)
            if key in aliases:
                sid = spell_circle_subject_id(circle_row["id"])
                return sid, str(circle_row.get("name") or f"Circle {circle_row['id']}")
            if any(key in alias for alias in aliases):
                sid = spell_circle_subject_id(circle_row["id"])
                spell_circle_matches.append((sid, str(circle_row.get("name") or f"Circle {circle_row['id']}")))
        if len(spell_circle_matches) == 1:
            return spell_circle_matches[0]
        if len(spell_circle_matches) > 1:
            spell_circle_matches.sort(key=lambda x: len(x[1]))
            return spell_circle_matches[0]

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
        await _show_skill_list(session, server)
        return

    # Parse "TRAIN <skill> [<n>]"
    parts = arg.rsplit(None, 1)
    rank_count = 1
    skill_arg  = arg
    if len(parts) == 2 and parts[1].isdigit():
        rank_count = max(1, min(int(parts[1]), 9999))
        skill_arg  = parts[0]

    skill_id, skill_name = resolve_skill(skill_arg, session=session, server=server)
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
    limit = get_train_limit(skill_id, prof_id)
    if is_spell_circle_subject(skill_id):
        circle_id = spell_circle_id_for_subject(skill_id)
        old_ranks = int((dict(getattr(session, "spell_ranks", {}) or {})).get(circle_id, 0) or 0)
        max_ranks = get_spell_circle_max_ranks(circle_id, session, server)
    else:
        max_ranks = get_max_ranks(skill_id, prof_id, level)
        skills = session.skills or {}
        current = skills.get(skill_id, {})
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
    if is_spell_circle_subject(skill_id):
        total_spell_ranks = get_total_spell_ranks(session, server, prof_id)
        total_ptp, total_mtp = cost_for_rank_range(
            ptp_base, mtp_base, limit, level, total_spell_ranks, total_spell_ranks + rank_count
        )
    else:
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

    session.physical_tp -= total_ptp
    session.mental_tp   -= total_mtp

    if server.db and session.character_id:
        if is_spell_circle_subject(skill_id):
            circle_id = spell_circle_id_for_subject(skill_id)
            if not session.spell_ranks:
                session.spell_ranks = {}
            session.spell_ranks[int(circle_id)] = new_ranks
            server.db.save_character_spell_ranks(session.character_id, session.spell_ranks)
            session.spellbook = server.db.load_character_spellbook(session.character_id)
            total_spell_ranks = get_total_spell_ranks(session, server, prof_id)
            if not session.skills:
                session.skills = {}
            session.skills[SPELL_RESEARCH_SKILL_ID] = {
                'ranks': total_spell_ranks,
                'bonus': calc_skill_bonus(total_spell_ranks),
            }
            server.db.save_character_skill(
                session.character_id,
                SPELL_RESEARCH_SKILL_ID,
                total_spell_ranks,
                calc_skill_bonus(total_spell_ranks),
            )
        else:
            if not session.skills:
                session.skills = {}
            session.skills[skill_id] = {
                'ranks': new_ranks,
                'bonus': new_bonus,
            }
            server.db.save_character_skill(
                session.character_id, skill_id, new_ranks, new_bonus
            )
        server.db.save_character_tps(
            session.character_id, session.physical_tp, session.mental_tp
        )
    elif not is_spell_circle_subject(skill_id):
        if not session.skills:
            session.skills = {}
        session.skills[skill_id] = {
            'ranks': new_ranks,
            'bonus': new_bonus,
        }
    else:
        circle_id = spell_circle_id_for_subject(skill_id)
        if not session.spell_ranks:
            session.spell_ranks = {}
        session.spell_ranks[int(circle_id)] = new_ranks
        total_spell_ranks = get_total_spell_ranks(session, server, prof_id)
        if not session.skills:
            session.skills = {}
        session.skills[SPELL_RESEARCH_SKILL_ID] = {
            'ranks': total_spell_ranks,
            'bonus': calc_skill_bonus(total_spell_ranks),
        }

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
        (
            f"  {skill_name}: {old_ranks} -> {new_ranks} ranks"
            if is_spell_circle_subject(skill_id)
            else f"  {skill_name}: {old_ranks} -> {new_ranks} ranks  (Bonus: +{new_bonus})"
        ),
        TextPresets.EXPERIENCE
    ))
    await session.send_line(colorize(
        f"  Remaining TPs: {session.physical_tp} physical, {session.mental_tp} mental",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(limit_note, TextPresets.SYSTEM))

    # ── Weapon Technique auto-grant ───────────────────────────────────────────
    if not is_spell_circle_subject(skill_id):
        await check_technique_grants(session, skill_id, new_ranks, server)


async def _show_skill_list(session, server=None):
    """Display all trainable skills with costs for this profession."""
    prof_id = getattr(session, 'profession_id', 1)
    level   = getattr(session, 'level', 1)
    skills_out, display_categories = build_training_catalog(session, server)

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

    for category, skill_ids in display_categories.items():
        await session.send_line(colorize(f"  -- {category} --", TextPresets.WARNING))
        for sid in skill_ids:
            skill_row = skills_out.get(int(sid))
            if not skill_row:
                continue
            name = str(skill_row.get("name") or SKILL_NAMES.get(sid) or f"Skill {sid}")
            ptp_b = int(skill_row.get("ptp", 0) or 0)
            mtp_b = int(skill_row.get("mtp", 0) or 0)
            max_r = int(skill_row.get("max_ranks", 0) or 0)
            show_bonus = bool(skill_row.get("show_bonus", True))

            if ptp_b == 0 and mtp_b == 0 and not bool(skill_row.get("trainable", False)):
                cost_str = colorize(f"{'--':>8}  {'--':>8}", TextPresets.COMBAT_MISS)
                cap_str  = "  --"
            else:
                cost_str = f"{ptp_b:>8}  {mtp_b:>8}"
                cap_str  = f"{max_r:>4}"

            ranks = int(skill_row.get("ranks", 0) or 0)
            bonus = int(skill_row.get("bonus", 0) or 0)
            bonus_str = f"{bonus:>5}" if show_bonus else f"{'--':>5}"

            await session.send_line(
                f"  {name:<30} {ranks:>4}  {bonus_str}  {cost_str}  {cap_str}"
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
