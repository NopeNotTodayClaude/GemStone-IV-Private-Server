"""
encumbrance.py
--------------
Encumbrance system with server-tunable coin weight.

Source: gswiki.play.net/Encumbrance  +  gswiki.play.net/Strength

Carry Capacity (pounds):
    cap = (STR_bonus + 20) * 4
    STR 50 (bonus  0) → 80 lbs
    STR 70 (bonus 10) → 120 lbs
    STR 100 (bonus 25) → 180 lbs
    STR 20 (bonus -15) → 20 lbs  (min 10)

Encumbrance Tiers  (% of capacity carried):
    NONE        0 – 32 %     No penalty
    SLIGHTLY   33 – 50 %     AS/DS -5,  RT +0
    MODERATELY 51 – 66 %     AS/DS -15, RT +1
    HEAVILY    67 – 80 %     AS/DS -25, RT +2
    SEVERELY   81 – 100 %    AS/DS -40, RT +3, movement speed halved
    OVERBURDENED 101 %+      AS/DS -60, RT +5, no running, stamina drain

Weight sources counted:
    • Items worn directly on the body (slot set, no container_id)
    • right_hand / left_hand items (held weapons/items)
    • Silver coins  (server-tuned via Lua, default 4800 coins = 1 lb)

Weight sources IGNORED:
    • Any item with container_id set — stowed inside a backpack, cloak,
      sack, or other container.  The container itself is worn and counted;
      its contents are not.  There is no inventory-management encumbrance
      penalty — only worn gear and held items create real encumbrance.

TWC note:
    The combat engine already applies the left-weapon WeightPenalty
    separately inside _calc_twc_rt().  Encumbrance is a *global* penalty
    on top of that; the two do not double-count because one is per-swing
    roundtime and the other is carried-weight fatigue.
"""

from typing import Tuple
from server.core.engine.material_weight import effective_weight as _material_effective_weight

# ── Encumbrance tier definitions ──────────────────────────────────────────────

TIER_NONE         = 0
TIER_SLIGHTLY     = 1
TIER_MODERATELY   = 2
TIER_HEAVILY      = 3
TIER_SEVERELY     = 4
TIER_OVERBURDENED = 5

TIER_NAMES = {
    TIER_NONE:         "None",
    TIER_SLIGHTLY:     "Slightly",
    TIER_MODERATELY:   "Moderately",
    TIER_HEAVILY:      "Heavily",
    TIER_SEVERELY:     "Severely",
    TIER_OVERBURDENED: "Overburdened",
}

# (min_pct, max_pct, tier)  — checked in order
_TIER_THRESHOLDS = [
    (0,   32,  TIER_NONE),
    (33,  50,  TIER_SLIGHTLY),
    (51,  66,  TIER_MODERATELY),
    (67,  80,  TIER_HEAVILY),
    (81,  100, TIER_SEVERELY),
    (101, 9999, TIER_OVERBURDENED),
]

# Combat penalties per tier
# (as_ds_penalty, rt_adder)
_TIER_COMBAT = {
    TIER_NONE:         (0,   0),
    TIER_SLIGHTLY:     (-5,  0),
    TIER_MODERATELY:   (-15, 1),
    TIER_HEAVILY:      (-25, 2),
    TIER_SEVERELY:     (-40, 3),
    TIER_OVERBURDENED: (-60, 5),
}

DEFAULT_COINS_PER_POUND = 4800.0


def _coins_per_pound(session) -> float:
    server = getattr(session, "server", None)
    lua_mgr = getattr(server, "lua", None)
    try:
        if lua_mgr:
            cfg = lua_mgr.get_encumbrance_cfg() or {}
            cpp = float(cfg.get("coins_per_pound", DEFAULT_COINS_PER_POUND))
            return max(1.0, cpp)
    except Exception:
        pass
    return DEFAULT_COINS_PER_POUND


# ── Core calculations ─────────────────────────────────────────────────────────

def carry_capacity(session) -> float:
    """
    Maximum carry weight in pounds.
    cap = max(10, (STR_bonus + 20) * 4)
    """
    str_val   = float(getattr(session, 'stat_strength', 50))
    str_bonus = (str_val - 50.0) / 2.0
    cap = (str_bonus + 20.0) * 4.0
    return max(10.0, cap)


def carried_weight(session) -> float:
    """
    Total weight currently carried in pounds.

    Counts:
      • Worn items  — equipped directly on the body (slot set, no container_id)
      • Held items  — right_hand / left_hand
      • Silver coins (server-tuned coins-per-pound ratio)

    Intentionally EXCLUDED:
      • Anything with container_id set — i.e. items stowed inside a backpack,
        cloak, sack, or any other container.  The container itself is worn on
        the body and its own weight is counted; its contents are not.
        This means you can carry 50,000 items in your backpack with zero
        encumbrance penalty — inventory management is not the point.
        Encumbrance only matters for what you are actually wearing or holding.
    """
    total = 0.0

    # Worn items only — skip anything inside a container.
    # _material_effective_weight() applies the material's weight_modifier so that
    # kelyn (0.7x), imflass (0.6x), golvern (0.5x), gornar (1.1x) etc. all weigh
    # their correct amount.  Falls back to raw weight if material is unknown.
    for item in getattr(session, 'inventory', []) or []:
        if item.get('container_id'):
            continue          # stowed inside a bag/cloak/etc — ignored
        total += _material_effective_weight(item)

    # Held items (stored separately from inventory list)
    for slot in ('right_hand', 'left_hand'):
        item = getattr(session, slot, None)
        if item:
            total += _material_effective_weight(item)

    # Silver coins (server-tuned ratio via Lua)
    silver = float(getattr(session, 'silver', 0) or 0)
    total += silver / _coins_per_pound(session)

    return total


def encumbrance_pct(session) -> float:
    """Carried weight as a percentage of carry capacity (0–200+ %)."""
    cap = carry_capacity(session)
    if cap <= 0:
        return 0.0
    return (carried_weight(session) / cap) * 100.0


def encumbrance_tier(session) -> int:
    """Return the TIER_* constant for the session's current encumbrance."""
    pct = encumbrance_pct(session)
    for lo, hi, tier in _TIER_THRESHOLDS:
        if lo <= pct <= hi:
            return tier
    return TIER_OVERBURDENED


def encumbrance_name(session) -> str:
    """Human-readable encumbrance tier name."""
    return TIER_NAMES[encumbrance_tier(session)]


def encumbrance_combat_penalties(session) -> Tuple[int, int]:
    """
    Returns (as_ds_penalty, rt_adder) for the current encumbrance tier.
    as_ds_penalty is negative (or 0).  rt_adder is non-negative.
    """
    tier = encumbrance_tier(session)
    return _TIER_COMBAT[tier]


def encumbrance_rt_penalty(session) -> int:
    """RT roundtime adder from encumbrance alone."""
    _, rt = encumbrance_combat_penalties(session)
    return rt


def encumbrance_as_ds_penalty(session) -> int:
    """AS/DS penalty (negative int, or 0) from encumbrance."""
    pen, _ = encumbrance_combat_penalties(session)
    return pen


def is_overburdened(session) -> bool:
    return encumbrance_tier(session) == TIER_OVERBURDENED


def is_movement_slowed(session) -> bool:
    """Severely or Overburdened: movement messages differ."""
    return encumbrance_tier(session) >= TIER_SEVERELY


# ── Display helpers ───────────────────────────────────────────────────────────

def format_weight_summary(session) -> str:
    """
    Single-line summary suitable for WEIGHT command or INFO display.
    Example:
        You are carrying 18.5 lbs of 80.0 lbs  [Slightly encumbered]
    """
    carried = carried_weight(session)
    cap     = carry_capacity(session)
    name    = encumbrance_name(session)
    tier    = encumbrance_tier(session)

    if tier == TIER_NONE:
        enc_str = "Not encumbered"
    elif tier == TIER_OVERBURDENED:
        enc_str = "OVERBURDENED"
    else:
        enc_str = f"{name} encumbered"

    return (
        f"  You are carrying {carried:.1f} lbs of {cap:.0f} lbs maximum.  "
        f"[{enc_str}]"
    )


def format_weight_detail(session) -> list:
    """
    Multi-line breakdown for WEIGHT DETAIL command.
    Returns list of strings.
    """
    carried = carried_weight(session)
    cap     = carry_capacity(session)
    pct     = encumbrance_pct(session)
    name    = encumbrance_name(session)
    tier    = encumbrance_tier(session)
    pen, rt = encumbrance_combat_penalties(session)

    # Per-item breakdown — only worn/held items (same rule as carried_weight)
    inv_items = [i for i in (getattr(session, 'inventory', []) or [])
                 if not i.get('container_id')]
    rh = getattr(session, 'right_hand', None)
    lh = getattr(session, 'left_hand',  None)
    held = [(rh, 'right hand'), (lh, 'left hand')]

    # Sort heaviest first
    all_items = [(float(i.get('weight') or 0),
                  i.get('short_name') or i.get('name') or 'item',
                  'carried')
                 for i in inv_items]
    for item, loc in held:
        if item:
            all_items.append((float(item.get('weight') or 0),
                               item.get('short_name') or item.get('name') or 'item',
                               loc))
    all_items.sort(reverse=True)

    silver = float(getattr(session, 'silver', 0) or 0)
    coin_w = silver / _coins_per_pound(session)

    lines = []
    lines.append(f"  Carry capacity  : {cap:.0f} lbs  (STR {getattr(session, 'stat_strength', 50)})")
    lines.append(f"  Currently carrying: {carried:.1f} lbs  ({pct:.0f}%  of capacity)")
    lines.append(f"  Status          : {name}")
    if pen < 0:
        lines.append(f"  Combat penalty  : AS/DS {pen:+d},  RT +{rt}")
    lines.append("")

    if all_items:
        lines.append("  Item breakdown (heaviest first):")
        for w, name_str, loc in all_items[:20]:
            lines.append(f"    {name_str:<36}  {w:>5.1f} lbs")
        if len(all_items) > 20:
            lines.append(f"    ... and {len(all_items)-20} more items.")

    if coin_w >= 0.1:
        lines.append(f"    {int(silver)} silver coins{'':<22}  {coin_w:>5.1f} lbs")

    return lines
