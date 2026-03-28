"""
status_effects.py  (combat shim)
---------------------------------
Backward-compatibility wrapper.

All effect state now lives in StatusManager (server.status).
This file keeps the old function-based API working so existing combat engine
code doesn't need to change.  New code should call server.status directly.

Old API preserved:
    apply_effect(entity, name, duration, stacks, magnitude)
    remove_effect(entity, name)
    has_effect(entity, name)   -> bool
    is_stunned(entity)         -> bool
    is_prone(entity)           -> bool
    get_combat_mods(entity)    -> (as_mod, ds_mod)
    apply_bleed(entity, severity, attacker)
    apply_poison(entity, magnitude, duration)
    apply_stun(entity, duration)
    apply_fear(entity, duration)
    apply_prone(entity, duration)

New convenience helpers (forward to StatusManager):
    apply_webbed(entity, duration)
    apply_blinded(entity, duration)
    apply_stagger(entity, duration)
    apply_demoralized(entity, duration)
    apply_major_bleed(entity, severity, attacker)
    apply_major_poison(entity, magnitude, duration)
    apply_disease(entity, magnitude, duration)
    apply_wound(entity, duration)
    apply_vulnerable(entity, duration)
    apply_slowed(entity, duration)
    apply_silenced(entity, duration)
    apply_daze(entity, duration)
    apply_disoriented(entity, duration)
    apply_crippled(entity, duration)
    apply_groggy(entity)
    clear_combat_debuffs(entity)
"""

import logging
import time
from typing import Tuple

log = logging.getLogger(__name__)

# ── Module-level server reference (set by game_server at boot) ────────────────
# game_server.py calls:  from server.core.engine.combat import status_effects
#                        status_effects._SERVER = self
_SERVER = None


def _mgr():
    """Return the StatusManager, or None if server not wired yet."""
    if _SERVER is not None:
        return getattr(_SERVER, "status", None)
    return None


def _buffed(entity, key: str) -> bool:
    if _SERVER is None:
        return False
    try:
        from server.core.engine.magic_effects import has_effect
        return has_effect(_SERVER, entity, key)
    except Exception:
        return False


# ── Legacy EFFECT_DEFS (kept for anything that imports the dict directly) ─────

EFFECT_DEFS = {
    "bleed":   {"tick_interval": 8,  "max_stacks": 5, "description": "Bleeding"},
    "poison":  {"tick_interval": 12, "max_stacks": 3, "description": "Poisoned"},
    "stun":    {"tick_interval": 1,  "max_stacks": 1, "description": "Stunned"},
    "stagger": {"tick_interval": 1,  "max_stacks": 1, "description": "Staggered"},
    "prone":   {"tick_interval": 1,  "max_stacks": 1, "description": "Prone"},
    "webbed":  {"tick_interval": 5,  "max_stacks": 1, "description": "Webbed"},
    "fear":    {"tick_interval": 3,  "max_stacks": 1, "description": "Frightened"},
}

# Legacy combat mods dict (retained for imports)
EFFECT_COMBAT_MODS = {
    "stun":    (-30, -30),
    "stagger": (-15, -15),
    "prone":   (-20, -25),
    "fear":    (-10, -10),
    "webbed":  (-10, -20),
    "bleed":   (0,    0),
    "poison":  (-5,  -5),
}

# Map old effect names to new StatusManager IDs
_NAME_MAP = {
    "bleed":   "bleeding",
    "stun":    "stunned",
    "stagger": "staggered",
    "fear":    "fear",
    "prone":   "prone",
    "webbed":  "webbed",
    "poison":  "poisoned",
}


def _resolve(name: str) -> str:
    """Map legacy short names to canonical StatusManager IDs."""
    return _NAME_MAP.get(name, name)


# ── Legacy core API ───────────────────────────────────────────────────────────

def apply_effect(entity, effect_name: str, duration: float,
                 stacks: int = 1, magnitude: float = 1):
    mgr = _mgr()
    if mgr:
        mgr.apply(entity, _resolve(effect_name), duration=duration,
                  stacks=stacks, magnitude=magnitude)
        return
    # Bare fallback — write directly to entity.status_effects dict
    _fallback_apply(entity, effect_name, duration, stacks, magnitude)


def remove_effect(entity, effect_name: str):
    mgr = _mgr()
    if mgr:
        mgr.remove(entity, _resolve(effect_name))
        return
    if hasattr(entity, "status_effects") and entity.status_effects:
        entity.status_effects.pop(effect_name, None)
        entity.status_effects.pop(_resolve(effect_name), None)


def has_effect(entity, effect_name: str) -> bool:
    mgr = _mgr()
    if mgr:
        return mgr.has(entity, _resolve(effect_name))
    # Bare fallback
    effects = getattr(entity, "status_effects", {}) or {}
    for name in (effect_name, _resolve(effect_name)):
        entry = effects.get(name)
        if entry:
            if isinstance(entry, dict):
                return time.time() < entry.get("expires", 0)
            return entry.active
    return False


def get_combat_mods(entity) -> Tuple[int, int]:
    """
    Legacy API: returns (as_mod, ds_mod) only.
    New code should call server.status.get_combat_mods(entity) for full tuple.
    """
    mgr = _mgr()
    if mgr:
        as_mod, ds_mod, *_ = mgr.get_combat_mods(entity)
        return as_mod, ds_mod
    # Bare fallback
    effects = getattr(entity, "status_effects", {}) or {}
    as_mod = ds_mod = 0
    for name in effects:
        mods = EFFECT_COMBAT_MODS.get(name, (0, 0))
        as_mod += mods[0]
        ds_mod += mods[1]
    return as_mod, ds_mod


def is_stunned(entity) -> bool:
    return has_effect(entity, "stunned")


def is_prone(entity) -> bool:
    pos = getattr(entity, "position", "standing")
    return pos == "lying" or has_effect(entity, "prone")


# ── Convenience apply helpers ─────────────────────────────────────────────────

def apply_bleed(entity, severity: int, attacker=None):
    """Apply bleed based on crit severity (1–9)."""
    if severity < 3:
        return
    stacks    = max(1, severity // 2)
    magnitude = max(1, severity - 2)
    duration  = 60 + severity * 15
    apply_effect(entity, "bleeding", duration, stacks=stacks, magnitude=magnitude)
    if attacker:
        entity.last_attacker = attacker


def apply_major_bleed(entity, severity: int, attacker=None):
    """Apply major bleed for high-crit scenarios."""
    if severity < 6:
        return apply_bleed(entity, severity, attacker)
    stacks   = max(1, severity // 2)
    duration = 90 + severity * 15
    apply_effect(entity, "major_bleed", duration, stacks=stacks, magnitude=severity)
    if attacker:
        entity.last_attacker = attacker


def apply_poison(entity, magnitude: float = 60.0, duration: float = 120.0):
    """Standard poison: magnitude = initial damage/tick, dissipates -5/tick."""
    if _buffed(entity, "poison_resist") or _buffed(entity, "gas_immune"):
        return
    apply_effect(entity, "poisoned", duration, stacks=1, magnitude=magnitude)


def apply_major_poison(entity, magnitude: float = 1.0, duration: float = 180.0):
    """Major poison: magnitude = stack count for % health damage."""
    if _buffed(entity, "poison_resist") or _buffed(entity, "gas_immune"):
        return
    apply_effect(entity, "major_poison", duration, stacks=int(magnitude), magnitude=1)


def apply_disease(entity, magnitude: float = 3.0, duration: float = 600.0):
    apply_effect(entity, "disease", duration, stacks=1, magnitude=magnitude)


def apply_stun(entity, duration: float):
    """Apply stun (does not stack or refresh — GS4 canonical)."""
    apply_effect(entity, "stunned", duration, stacks=1)


def apply_fear(entity, duration: float = 30.0):
    if _buffed(entity, "fear_immune"):
        return
    apply_effect(entity, "fear", duration, stacks=1)


def apply_prone(entity, duration: float = 15.0):
    apply_effect(entity, "prone", duration, stacks=1)
    if hasattr(entity, "position"):
        entity.position = "lying"


def apply_webbed(entity, duration: float = 30.0):
    apply_effect(entity, "webbed", duration, stacks=1)


def apply_blinded(entity, duration: float = 30.0):
    apply_effect(entity, "blinded", duration, stacks=1)


def apply_stagger(entity, duration: float = 10.0):
    apply_effect(entity, "staggered", duration, stacks=1)


def apply_demoralized(entity, duration: float = 60.0):
    apply_effect(entity, "demoralized", duration, stacks=1)


def apply_wound(entity, duration: float = 300.0):
    apply_effect(entity, "wounded", duration, stacks=1)


def apply_vulnerable(entity, duration: float = 30.0):
    apply_effect(entity, "vulnerable", duration, stacks=1)


def apply_slowed(entity, duration: float = 20.0):
    apply_effect(entity, "slowed", duration, stacks=1)


def apply_silenced(entity, duration: float = 30.0):
    apply_effect(entity, "silenced", duration, stacks=1)


def apply_daze(entity, duration: float = 10.0):
    apply_effect(entity, "dazed", duration, stacks=1)


def apply_disoriented(entity, duration: float = 15.0):
    apply_effect(entity, "disoriented", duration, stacks=1)


def apply_crippled(entity, duration: float = 60.0):
    apply_effect(entity, "crippled", duration, stacks=1)


def apply_groggy(entity):
    """Post-sleep grogginess (from Sleep 501 air lore wakeup)."""
    apply_effect(entity, "groggy", 10.0, stacks=1)


def apply_mind_rot(entity, magnitude: float = 2.0, duration: float = 300.0):
    apply_effect(entity, "mind_rot", duration, stacks=1, magnitude=magnitude)


def clear_combat_debuffs(entity):
    """Remove all DEBUFF_COMBAT and DEBUFF_STAT effects (e.g. on raise/death)."""
    mgr = _mgr()
    if mgr:
        mgr.clear_all(entity, "DEBUFF_COMBAT")
        mgr.clear_all(entity, "DEBUFF_STAT")
        mgr.clear_all(entity, "DEBUFF_CONTROL")
        return
    if hasattr(entity, "status_effects"):
        entity.status_effects = {}


# ── StatusEffectManager shim (legacy class still importable) ─────────────────

class StatusEffectManager:
    """
    Legacy class kept for any code that instantiates it directly.
    All ticking is now handled by StatusManager.tick().
    This class delegates immediately to server.status.
    """

    def __init__(self, server):
        self._server = server
        global _SERVER
        _SERVER = server

    async def tick(self, tick_count: int):
        mgr = _mgr()
        if mgr:
            await mgr.tick(tick_count)

    # ── Creature flee / death kept here for any direct callers ───────────────
    async def _creature_flee(self, creature):
        mgr = _mgr()
        if mgr:
            await mgr._creature_flee(creature)

    async def _creature_bleed_death(self, creature):
        mgr = _mgr()
        if mgr:
            await mgr._creature_dot_death(creature, "bleed")


# ── Bare fallback (no server wired) ──────────────────────────────────────────

def _fallback_apply(entity, effect_name: str, duration: float,
                    stacks: int, magnitude: float):
    """Direct dict write when StatusManager is not yet available."""
    if not hasattr(entity, "status_effects") or entity.status_effects is None:
        entity.status_effects = {}
    now = time.time()
    canonical = _resolve(effect_name)
    defn = EFFECT_DEFS.get(effect_name, EFFECT_DEFS.get(canonical, {}))
    max_stacks = defn.get("max_stacks", 1)
    tick_iv    = defn.get("tick_interval", 1)
    if canonical in entity.status_effects:
        ex = entity.status_effects[canonical]
        if isinstance(ex, dict):
            ex["expires"]   = max(ex.get("expires", 0), now + duration)
            ex["stacks"]    = min(max_stacks, ex.get("stacks", 1) + stacks)
            ex["magnitude"] = max(ex.get("magnitude", 1), magnitude)
    else:
        entity.status_effects[canonical] = {
            "expires":       now + duration,
            "stacks":        min(max_stacks, stacks),
            "magnitude":     magnitude,
            "last_tick":     now,
            "tick_interval": tick_iv,
        }
