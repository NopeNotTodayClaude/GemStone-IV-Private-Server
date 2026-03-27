"""
perception_loader.py
--------------------
Loads perception system configuration from scripts/globals/perception.lua.

Returns a flat dict of all tuning values. The command handlers
(combat.py, movement.py) import get_perception_cfg() to access these
rather than hardcoding numbers in Python.

Falls back to safe defaults if Lua is unavailable so the server
can still boot without perception being completely broken.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)

# Safe defaults — mirrors perception.lua values exactly.
# Only used if Lua engine is unavailable at runtime.
_DEFAULTS = {
    "skill_id":              27,
    "rank_multiplier":       3,
    "stat":                  "stat_intuition",
    "stat_divisor":          2,
    "hide_hider_bonus":      20,
    "hide_observer_mod":     0,
    "dark_penalty":          -20,
    "outdoor_penalty":       -10,
    "sneak_hider_bonus":     15,
    "sneak_observer_mod":    0,
    "search_level_mult":     0.5,
    "search_reveal_duration": 0,
    "search_nothing_msg":    "You search around carefully but find nothing hidden.",
    "search_found_exit_msg": "Your careful search reveals a hidden path: ",
    "search_failed_exit_msg":"You sense there may be something hidden here, but can't quite make it out.",
    "sense_threshold":       15,
}


def load_perception_cfg(lua_engine) -> dict:
    """
    Load perception config from Lua.
    Returns a dict with all tuning values.
    Falls back to _DEFAULTS on any failure — never raises.
    """
    if not lua_engine or not lua_engine.available:
        log.warning("perception_loader: Lua engine unavailable — using defaults")
        return dict(_DEFAULTS)

    try:
        data = lua_engine.load_data("globals/perception")
        if not data:
            log.warning("perception_loader: Lua returned no data — using defaults")
            return dict(_DEFAULTS)

        cfg = dict(_DEFAULTS)  # start from defaults, override with Lua values

        for key in _DEFAULTS:
            if key in data:
                val = data[key]
                # Coerce numerics
                if isinstance(_DEFAULTS[key], int) and not isinstance(_DEFAULTS[key], bool):
                    try:
                        cfg[key] = int(val)
                    except (TypeError, ValueError):
                        pass
                elif isinstance(_DEFAULTS[key], float):
                    try:
                        cfg[key] = float(val)
                    except (TypeError, ValueError):
                        pass
                elif isinstance(_DEFAULTS[key], str):
                    cfg[key] = str(val)
                else:
                    cfg[key] = val

        log.info("perception_loader: loaded perception config from Lua")
        return cfg

    except Exception as e:
        log.warning("perception_loader: failed to load Lua config (%s) — using defaults", e)
        return dict(_DEFAULTS)
