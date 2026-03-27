"""
server/core/engine/combat/material_combat.py
--------------------------------------------
Python bridge between combat_engine.py and the Lua-driven material systems:
flare procs, crit resolution, and weight calculation.

Design principles:
  • All game logic lives in Lua.  This file is pure wiring.
  • Every public function degrades gracefully if Lua is unavailable.
  • Flare counters are stored on the session object so the shared Lua
    runtime stays stateless.
  • Weight modifier cache lives in material_weight.py (outside this package)
    to avoid a circular import with encumbrance.py.

Public API
----------
  # Weight (delegates to material_weight — no circular import risk):
  def effective_weight(item) -> float

  # Called per swing on a hit:
  async def resolve_flare(session, creature, weapon, hand) -> dict | None
  async def resolve_armor_flare(session, creature, armor, shield) -> dict | None

  # Called per hit before crit divisor:
  def get_crit_phantom(weapon, lua_engine) -> int
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)

# Weight is handled by material_weight.py to avoid circular imports.
# Re-export effective_weight so callers that already imported it from here
# don't break.
from server.core.engine.material_weight import effective_weight  # noqa: F401


# ── Flare proc ─────────────────────────────────────────────────────────────────

# Hit counters stored per session.  Structure:
#   session._flare_hit_counts = { 'right': int, 'left': int }
# Incremented on every successful hit.  The Lua flare_system checks
# (hit_count % FLARE_SWING_INTERVAL == 0) — so we pass the raw count and
# let Lua own the math.

def _get_flare_counter(session, hand: str) -> int:
    """Return the current hit count for a hand slot, incrementing it."""
    if not hasattr(session, "_flare_hit_counts"):
        session._flare_hit_counts = {"right": 0, "left": 0}
    session._flare_hit_counts[hand] = session._flare_hit_counts.get(hand, 0) + 1
    return session._flare_hit_counts[hand]


async def resolve_flare(session, creature, weapon: dict, hand: str) -> Optional[dict]:
    """
    Attempt a flare proc for this hit.

    Args:
        session:  player session (has session.server.lua and session.name)
        creature: creature object (has .name, .family, .take_damage)
        weapon:   item dict for the weapon (has 'material', 'noun', 'flare_type')
        hand:     'right' or 'left'

    Returns:
        None if no flare procced, or a dict:
        {
            'proc':         True,
            'flare_type':   str,
            'crit_rank':    int,
            'damage':       int,
            'vuln_mult':    float,
            'attacker_msg': str,
            'room_msg':     str,
        }

    The caller (combat_engine.py) must:
        1. creature.take_damage(result['damage'])
        2. await session.send_line(result['attacker_msg'])
        3. broadcast result['room_msg'] to the room (excluding attacker)
    """
    if not weapon:
        return None

    # Fast out — no flare_type on this weapon (covers non-flare materials)
    flare_type = weapon.get("flare_type") or ""
    if not flare_type:
        return None

    lua_engine = getattr(getattr(session, "server", None), "lua", None)
    if not lua_engine or not lua_engine.engine:
        return None

    try:
        hit_count = _get_flare_counter(session, hand)

        flare_module = lua_engine.engine.require("globals/combat/flare_system")
        if not flare_module:
            return None

        weapon_table   = lua_engine.engine.python_to_lua(weapon)
        creature_table = lua_engine.engine.python_to_lua({
            "name":   getattr(creature, "name", "the creature"),
            "family": getattr(creature, "family", ""),
        })

        raw_result = flare_module.tryFlare(
            weapon_table,
            creature_table,
            hit_count,
            getattr(session, "name", "Someone"),
        )

        result = lua_engine.engine.lua_to_python(raw_result)

        if not result or not result.get("proc"):
            return None

        return result

    except Exception as e:
        log.error("material_combat.resolve_flare: %s", e)
        return None


async def resolve_armor_flare(session, creature, armor: Optional[dict], shield: Optional[dict]) -> Optional[dict]:
    """
    Attempt a defensive flare proc when the player is hit by a creature.
    Checks worn armor first, then shield — first one with a flare_type wins.

    Armor/shield flares use the same counter system as weapon flares but tracked
    under the 'armor' and 'shield' slots on the session hit counter.

    Args:
        session:  player session
        creature: the attacking creature (flare damage applied to it)
        armor:    player's worn armor item dict (may be None)
        shield:   player's worn shield item dict (may be None)

    Returns:
        None if no flare, or same dict format as resolve_flare with
        attacker_msg framed from the defender's perspective.
    """
    lua_engine = getattr(getattr(session, "server", None), "lua", None)
    if not lua_engine or not lua_engine.engine:
        return None

    # Pick whichever item has a flare_type — armor takes priority over shield
    flare_item = None
    flare_slot = None
    for item, slot in ((armor, "armor"), (shield, "shield")):
        if item and (item.get("flare_type") or ""):
            flare_item = item
            flare_slot = slot
            break

    if not flare_item:
        return None

    try:
        hit_count = _get_flare_counter(session, flare_slot)

        flare_module = lua_engine.engine.require("globals/combat/flare_system")
        if not flare_module:
            return None

        item_table     = lua_engine.engine.python_to_lua(flare_item)
        creature_table = lua_engine.engine.python_to_lua({
            "name":   getattr(creature, "name", "the creature"),
            "family": getattr(creature, "family", ""),
        })

        # For armor flares the "weapon" passed to tryFlare is the armor/shield item.
        # The noun field will say e.g. "breastplate" or "shield" in the message.
        raw_result = flare_module.tryFlare(
            item_table,
            creature_table,
            hit_count,
            getattr(session, "name", "Someone"),
        )

        result = lua_engine.engine.lua_to_python(raw_result)

        if not result or not result.get("proc"):
            return None

        # Rephrase attacker_msg to be from the defender's perspective
        orig = result.get("attacker_msg", "")
        result["attacker_msg"] = orig.replace("Your ", "Your ").replace(
            "erupts from your", "erupts from your"
        )  # messages already say "Your X flares" which works for defender too

        return result

    except Exception as e:
        log.error("material_combat.resolve_armor_flare: %s", e)
        return None


# ── Crit phantom damage (razern CEP) ──────────────────────────────────────────

def get_crit_phantom(weapon: dict, lua_engine) -> int:
    """
    Returns the crit_weight phantom damage points for the weapon's material.
    0 for all materials except razern (2).

    This is called BEFORE the crit rank formula:
        adjusted_raw = raw_damage + get_crit_phantom(weapon, lua)
        crit_rank_max = min(cap, adjusted_raw // crit_divisor)
    HP damage uses original raw_damage, not adjusted_raw.

    Args:
        weapon:     item dict (has 'material')
        lua_engine: server.lua  (LuaManager instance)

    Returns:
        int: phantom damage points to add (0 if unknown or Lua unavailable)
    """
    material = (weapon.get("material") or "").lower()
    if not material:
        return 0

    if not lua_engine or not lua_engine.engine:
        return 0

    try:
        resolver = lua_engine.engine.require("globals/combat/crit_resolver")
        if not resolver:
            return 0
        raw = resolver.quickCritWeight(material)
        return int(raw or 0)
    except Exception as e:
        log.error("material_combat.get_crit_phantom: %s", e)
        return 0
