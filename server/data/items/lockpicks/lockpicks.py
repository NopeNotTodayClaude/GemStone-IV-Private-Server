"""
GemStone IV Lockpick Material Data
Source: gswiki.play.net/Lockpick

Each material has a modifier RANGE (mod_min, mod_max).
When a pick is first used, a specific modifier is rolled within that range
and stored in extra_data['pick_modifier'] -- it never changes after that.

modifier_mid - the typical/catalog value shown in DETECT output description
mod_min      - lowest possible roll for this material
mod_max      - highest possible roll for this material
min_ranks    - minimum Picking Locks ranks required to use without penalty
strength     - durability tier (1=flimsy ... 11=astonishingly strong)
price        - base shop price in silver
precision    - descriptive label used in DETECT output

NOTE: "bronze" is not a GS4 lockpick material -- aliased to brass.
"""

import random

LOCKPICK_MATERIALS = {
    "copper":  {"modifier_mid": 1.00, "mod_min": 0.97, "mod_max": 1.05,
                "min_ranks":  0, "strength":  2, "price":    100, "precision": "very inaccurate"},
    "brass":   {"modifier_mid": 1.05, "mod_min": 1.02, "mod_max": 1.11,
                "min_ranks":  0, "strength":  2, "price":    250, "precision": "very inaccurate"},
    "steel":   {"modifier_mid": 1.10, "mod_min": 1.07, "mod_max": 1.16,
                "min_ranks":  1, "strength":  4, "price":    500, "precision": "inaccurate"},
    "gold":    {"modifier_mid": 1.20, "mod_min": 1.16, "mod_max": 1.26,
                "min_ranks":  3, "strength":  3, "price":   2000, "precision": "somewhat inaccurate"},
    "ivory":   {"modifier_mid": 1.20, "mod_min": 1.15, "mod_max": 1.27,
                "min_ranks":  1, "strength":  5, "price":    750, "precision": "somewhat inaccurate"},
    "silver":  {"modifier_mid": 1.30, "mod_min": 1.26, "mod_max": 1.36,
                "min_ranks":  3, "strength":  4, "price":   2500, "precision": "inefficient"},
    "mithril": {"modifier_mid": 1.45, "mod_min": 1.40, "mod_max": 1.52,
                "min_ranks":  5, "strength":  8, "price":   6000, "precision": "unreliable"},
    "ora":     {"modifier_mid": 1.55, "mod_min": 1.50, "mod_max": 1.62,
                "min_ranks":  5, "strength":  7, "price":   5000, "precision": "below average"},
    "glaes":   {"modifier_mid": 1.60, "mod_min": 1.55, "mod_max": 1.68,
                "min_ranks":  8, "strength": 10, "price":   9500, "precision": "average"},
    "laje":    {"modifier_mid": 1.75, "mod_min": 1.69, "mod_max": 1.83,
                "min_ranks": 12, "strength":  4, "price":  17000, "precision": "above average"},
    "vultite": {"modifier_mid": 1.80, "mod_min": 1.74, "mod_max": 1.88,
                "min_ranks": 20, "strength":  4, "price":  30000, "precision": "somewhat accurate"},
    "rolaren": {"modifier_mid": 1.90, "mod_min": 1.84, "mod_max": 1.98,
                "min_ranks": 12, "strength":  8, "price":  17000, "precision": "favorable"},
    "veniom":  {"modifier_mid": 2.20, "mod_min": 2.13, "mod_max": 2.27,
                "min_ranks": 25, "strength":  9, "price":  50000, "precision": "highly accurate"},
    "invar":   {"modifier_mid": 2.25, "mod_min": 2.18, "mod_max": 2.34,
                "min_ranks": 35, "strength": 10, "price":  75000, "precision": "highly accurate"},
    "alum":    {"modifier_mid": 2.30, "mod_min": 2.22, "mod_max": 2.38,
                "min_ranks": 16, "strength":  3, "price":  23000, "precision": "excellent"},
    "golvern": {"modifier_mid": 2.35, "mod_min": 2.27, "mod_max": 2.42,
                "min_ranks": 40, "strength": 11, "price":  95000, "precision": "excellent"},
    "kelyn":   {"modifier_mid": 2.40, "mod_min": 2.32, "mod_max": 2.48,
                "min_ranks": 25, "strength":  8, "price":  62000, "precision": "incredible"},
    "vaalin":  {"modifier_mid": 2.50, "mod_min": 2.35, "mod_max": 2.55,
                "min_ranks": 50, "strength": 10, "price": 125000, "precision": "unsurpassed"},
}

_MATERIAL_ALIASES = {"bronze": "brass"}

LOCKPICK_CONDITIONS = {
    5: {"label": "in excellent condition", "modifier_mult": 1.00},
    4: {"label": "in good condition",      "modifier_mult": 0.95},
    3: {"label": "in a neglected state",   "modifier_mult": 0.85},
    2: {"label": "noticeably damaged",     "modifier_mult": 0.70},
    1: {"label": "in poor condition",      "modifier_mult": 0.50},
    0: {"label": "broken",                 "modifier_mult": 0.00},
}


def _resolve_material(raw: str) -> str:
    mat = raw.lower().strip()
    return _MATERIAL_ALIASES.get(mat, mat)


def get_material_data(item: dict) -> dict:
    for key in ("pick_material", "material"):
        raw = (item.get(key) or "").strip()
        if raw:
            mat = _resolve_material(raw)
            if mat in LOCKPICK_MATERIALS:
                return LOCKPICK_MATERIALS[mat]
    name = (item.get("name") or item.get("short_name") or "").lower()
    for mat_key in LOCKPICK_MATERIALS:
        if mat_key in name:
            return LOCKPICK_MATERIALS[mat_key]
    for alias, target in _MATERIAL_ALIASES.items():
        if alias in name:
            return LOCKPICK_MATERIALS[target]
    return LOCKPICK_MATERIALS["copper"]


def roll_pick_modifier(item: dict) -> float:
    """Roll and store a specific modifier for this pick instance within its material range."""
    mat   = get_material_data(item)
    lo    = mat["mod_min"]
    hi    = mat["mod_max"]
    steps = round((hi - lo) / 0.01)
    rolled = round(lo + random.randint(0, steps) * 0.01, 2)
    item["pick_modifier"] = rolled
    return rolled


def get_pick_modifier(item: dict) -> float:
    """Return this pick's specific modifier, rolling it on first use."""
    val = item.get("pick_modifier")
    if val:
        return float(val)
    return roll_pick_modifier(item)


def get_condition(item: dict) -> dict:
    cond = item.get("pick_condition", 5)
    return LOCKPICK_CONDITIONS.get(int(cond), LOCKPICK_CONDITIONS[5])


def effective_modifier(item: dict) -> float:
    """This pick's specific rolled modifier * condition multiplier."""
    base = get_pick_modifier(item)
    cond = get_condition(item)
    return round(base * cond["modifier_mult"], 3)


def rank_penalty(item: dict, actual_ranks: int) -> int:
    mat = get_material_data(item)
    return max(0, (mat["min_ranks"] - actual_ranks) * 5)


def bend_chance(endroll: int, strength: int = 2) -> float:
    """
    Probability of bending pick on a failed attempt (endroll <= 60).
    Strength (1-11) reduces the chance — a golvern (11) bends far less than copper (2).
    Formula: base_chance * (1 - (strength - 1) / 14)
      strength  2 (copper/brass) -> x0.93 of base  (almost no reduction)
      strength  5 (ivory)        -> x0.71 of base
      strength  8 (mithril)      -> x0.50 of base
      strength 10 (glaes/invar)  -> x0.36 of base
      strength 11 (golvern)      -> x0.29 of base
    Intentionally reduced base from vanilla GS4 -- single-player server adjustment.
    """
    if endroll > 60:
        return 0.0
    if endroll < 0:
        base = 0.50
    else:
        base = min(0.50, 0.08 + (60 - endroll) / 240.0)

    # Strength divisor: strength 1=full chance, strength 11=29% of base
    str_factor = max(0.29, 1.0 - (strength - 1) / 14.0)
    return round(base * str_factor, 4)
