"""
ambush_loader.py
----------------
Loads ambush system configuration from scripts/globals/ambush.lua.

Returns a nested dict of tuning values used by combat resolution for:
  - hidden ambush aiming
  - hidden ambush defense pushdown
  - hidden ambush crit weighting
  - open aimed melee targeting

Falls back to defaults if Lua is unavailable so the server can still boot.
"""

import logging

log = logging.getLogger(__name__)

_DEFAULTS = {
    "skill_id": 26,
    "cm_skill_id": 4,
    "hidden": {
        "aim_bonus_mult": 0.25,
        "threshold_level_mult": 2.0,
        "threshold_flat": 0,
        "ebp_ds_share": 0.30,
        "ebp_reduction_pct": 0.50,
        "stance_pushdown": {
            "minimum_steps": 1,
            "level_scale": 3,
            "bonus_step_every": 60,
            "max_steps": 4,
        },
        "any_weapon_as_bonus": 2,
        "weapon_as_bonus": {
            "edged": 1,
            "blunt": 0,
            "twohanded": 0,
            "polearm": 0,
            "ranged": 0,
            "thrown": 0,
            "brawling": 0,
        },
        "favored_weapons": {
            "dagger": {"as_bonus": 5, "crit_flat": 8},
            "main gauche": {"as_bonus": 4, "crit_flat": 6},
            "katar": {"as_bonus": 3, "crit_flat": 4},
        },
        "crit_weighting": {
            "bonus_divisor": 30,
            "rank_divisor": 12,
            "any_weapon_flat": 1,
            "weapon_bonus": {
                "edged": 2,
                "blunt": 1,
                "twohanded": 1,
                "polearm": 1,
                "ranged": 1,
                "thrown": 1,
                "brawling": 1,
            },
        },
        "rt_reduction": 1,
    },
    "open_aim": {
        "ambush_bonus_mult": 0.25,
        "cm_bonus_mult": 0.25,
        "threshold_level_mult": 2.0,
        "threshold_flat": 0,
    },
}


def _merge_defaults(defaults, overrides):
    if not isinstance(defaults, dict):
        return overrides if overrides is not None else defaults
    merged = {}
    overrides = overrides if isinstance(overrides, dict) else {}
    for key, default_val in defaults.items():
        if key in overrides:
            if isinstance(default_val, dict):
                merged[key] = _merge_defaults(default_val, overrides.get(key))
            else:
                merged[key] = overrides.get(key)
        else:
            merged[key] = default_val
    for key, override_val in overrides.items():
        if key not in merged:
            merged[key] = override_val
    return merged


def load_ambush_cfg(lua_engine) -> dict:
    """
    Load ambush config from Lua.
    Returns a nested dict with defaults filled in.
    """
    if not lua_engine or not lua_engine.available:
        log.warning("ambush_loader: Lua engine unavailable - using defaults")
        return _merge_defaults(_DEFAULTS, {})

    try:
        data = lua_engine.load_data("globals/ambush")
        if not data:
            log.warning("ambush_loader: Lua returned no data - using defaults")
            return _merge_defaults(_DEFAULTS, {})
        cfg = _merge_defaults(_DEFAULTS, data)
        log.info("ambush_loader: loaded ambush config from Lua")
        return cfg
    except Exception as e:
        log.warning("ambush_loader: failed to load Lua config (%s) - using defaults", e)
        return _merge_defaults(_DEFAULTS, {})
