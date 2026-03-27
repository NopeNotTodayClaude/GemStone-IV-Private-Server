"""
smr_engine.py
-------------
Python-native SMRv2 implementation.

Used by weapon_api.py as the authoritative math engine when resolving
weapon technique outcomes returned from Lua.  Lua's smr.lua handles the
roll itself; Python uses this module to:
  1. Apply effects from result tables to session/creature objects
  2. Resolve actual attack rolls for techniques that trigger standard hits
  3. Handle deferred AoE (Volley) at impact time

Mirrors the math in scripts/globals/utils/smr.lua exactly.
"""

import random
import math
import logging

log = logging.getLogger(__name__)


# ── Racial size modifiers to physical maneuver endroll (offense) ─────────────
# race_id -> endroll bonus
RACIAL_SIZE_OFF = {
    1:  10,   # Giantman
    2:  10,   # Half-Krolvin
    3:   5,   # Human
    4:   5,   # Dwarf
    5:   0,   # Half-Elf
    6:   0,   # Dark Elf
    7:   0,   # Erithian
    8:   0,   # Sylvankind
    9:  -5,   # Aelotoi
    10: -5,   # Elf
    12: -10,  # Forest Gnome
    13: -15,  # Halfling
    14: -20,  # Burghal Gnome
}

# Bonus dodging ranks for defense
RACIAL_DODGE_BONUS = {
    9: 30, 6: 30, 7: 30, 5: 30, 8: 30,  # +30 group
    10: 60, 12: 60, 13: 60,              # +60 group
    14: 80,                               # Burghal Gnome
}

# Maneuver knowledge offensive bonus by rank 1-5
MK_OFF = [0, 2, 4, 8, 12, 20]
# Maneuver knowledge defensive bonus by rank 1-5
MK_DEF = [0, 2, 4, 8, 12, 20]

# Stance modifiers
STANCE_DEF_MOD = {
    "offensive": -20, "advance": -10, "forward": 0,
    "neutral": 0, "guarded": 15, "defensive": 25,
}
STANCE_OFF_MOD = {
    "offensive": 20, "advance": 15, "forward": 10,
    "neutral": 0, "guarded": -10, "defensive": -20,
}


def skill_bonus_from_ranks(ranks: int) -> int:
    """GS4 canonical skill bonus formula."""
    ranks = max(0, int(ranks))
    bonus = 0
    steps = [(10, 5), (10, 4), (10, 3), (10, 2)]
    for cap, rate in steps:
        take   = min(ranks, cap)
        bonus += take * rate
        ranks -= take
        if ranks <= 0:
            return bonus
    bonus += ranks  # 41+: +1 per rank
    return bonus


def open_d100() -> int:
    """Open-ended d100 roll as per GS4."""
    roll = random.randint(1, 100)
    if roll >= 96:
        roll += random.randint(1, 100)
    elif roll <= 5:
        roll -= random.randint(1, 100)
    return roll


def _sr(entity, skill: str) -> int:
    """Get skill ranks from entity (session or creature dict)."""
    if hasattr(entity, 'skills'):
        d = (entity.skills or {}).get(skill)
        if isinstance(d, dict):
            return int(d.get('ranks', 0))
        return int(d or 0)
    sr = getattr(entity, 'skill_ranks', {}) or {}
    return int(sr.get(skill, 0))


def _stat(entity, stat: str) -> int:
    """Get a stat value from entity."""
    if hasattr(entity, 'stats'):
        st = (entity.stats or {})
        if isinstance(st, dict):
            return int(st.get(stat, 0))
    return 0


def compute_defense(entity, opts: dict) -> int:
    """Compute SMRv2 defense bonus for an entity."""
    race_id      = int(getattr(entity, 'race_id', 0) or 0)
    racial_dodge = RACIAL_DODGE_BONUS.get(race_id, 0)

    dodge  = _sr(entity, 'dodging') + racial_dodge
    cm     = _sr(entity, 'combat_maneuvers')
    perc   = _sr(entity, 'perception')
    pf     = _sr(entity, 'physical_fitness')
    shield = _sr(entity, 'shield_use') if opts.get('include_shield') else 0

    skill_count = 5 if opts.get('include_shield') else 4
    avg_ranks   = (dodge + cm + perc + pf + shield) / skill_count
    skill_def   = skill_bonus_from_ranks(int(avg_ranks))

    agi  = _stat(entity, 'agility')
    dex  = _stat(entity, 'dexterity')
    itn  = _stat(entity, 'intuition')
    stat_def = int(agi * 0.6 + (dex + itn) * 0.2)

    stance_str = getattr(entity, 'stance', 'neutral') or 'neutral'
    stance_bonus = STANCE_DEF_MOD.get(stance_str, 0)

    spell_bonus = int(getattr(entity, 'smr_def_bonus', 0) or 0)

    enc_pen   = int(getattr(entity, 'encumbrance_penalty', 0) or 0)
    armor_pen = int(getattr(entity, 'armor_action_penalty', 0) or 0)

    mk_rank  = int(opts.get('defender_mk_rank', 0) or 0)
    mk_bonus = MK_DEF[mk_rank] if 0 < mk_rank <= 5 else 0

    return skill_def + stat_def + stance_bonus + spell_bonus + mk_bonus - enc_pen - armor_pen


def compute_offense(entity, opts: dict) -> int:
    """Compute SMRv2 offense bonus for an entity."""
    cm_ranks  = _sr(entity, 'combat_maneuvers')
    wpn_ranks = int(opts.get('weapon_skill_ranks', 0) or 0)

    level = max(1, int(getattr(entity, 'level', 1) or 1))

    def effective(r):
        if r > level:
            return level + int((r - level) * 0.85)
        return r

    avg_ranks = (effective(cm_ranks) + effective(wpn_ranks)) / 2
    skill_off = skill_bonus_from_ranks(int(avg_ranks))

    # Minimum level effectiveness
    min_off = level * 3
    if skill_off < min_off:
        skill_off = min_off

    stance_str    = getattr(entity, 'stance', 'neutral') or 'neutral'
    stance_bonus  = STANCE_OFF_MOD.get(stance_str, 0)

    racial_bonus = RACIAL_SIZE_OFF.get(int(getattr(entity, 'race_id', 0) or 0), 0) \
                   if opts.get('use_racial_size') else 0

    wpn_bonus = int(getattr(entity, 'smr_off_bonus', 0) or 0)

    mk_rank  = int(opts.get('attacker_mk_rank', 0) or 0)
    mk_bonus = MK_OFF[mk_rank] if 0 < mk_rank <= 5 else 0

    enc_pen   = int(getattr(entity, 'encumbrance_penalty', 0) or 0)
    armor_pen = int(getattr(entity, 'armor_action_penalty', 0) or 0)

    return skill_off + stance_bonus + racial_bonus + wpn_bonus + mk_bonus - enc_pen - armor_pen


def smr_roll(attacker, defender, opts: dict) -> dict:
    """Full SMRv2 roll. Returns result dict matching Lua SMR.roll() output."""
    off      = compute_offense(attacker, opts)
    def_     = compute_defense(defender, opts)
    d100     = open_d100()

    extra_off = int(opts.get('off_bonus', 0) or 0)
    extra_def = int(opts.get('def_bonus', 0) or 0)

    if opts.get('bypass_ebp'):
        stance_str  = getattr(defender, 'stance', 'neutral') or 'neutral'
        extra_def  -= STANCE_DEF_MOD.get(stance_str, 0)

    bonus = off - def_ + extra_off - extra_def
    total = d100 + bonus
    margin = total - 100

    return {
        'total':   total,
        'margin':  margin,
        'success': total > 100,
        'd100':    d100,
        'offense': off + extra_off,
        'defense': def_ + extra_def,
        'bonus':   bonus,
        'msg':     f"[SMR result: {total} (Open d100: {d100}, Bonus: {bonus})]",
    }


def technique_rank_from_skill(weapon_ranks: int, thresholds: list) -> int:
    """Return technique rank (0-5) based on weapon skill ranks."""
    weapon_ranks = int(weapon_ranks)
    for i, t in enumerate(reversed(thresholds), 1):
        if weapon_ranks >= int(t):
            return len(thresholds) - i + 1
    return 0


def moc_hits(moc_ranks: int) -> int:
    """Number of assault/AoE hits based on MOC ranks. 1 base + 1 per 40 ranks."""
    return 1 + max(0, int(moc_ranks) // 40)
