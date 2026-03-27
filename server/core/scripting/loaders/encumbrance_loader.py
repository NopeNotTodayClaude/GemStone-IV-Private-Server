"""
encumbrance_loader.py
---------------------
Loads encumbrance tuning from scripts/globals/encumbrance.lua.
"""

import logging

log = logging.getLogger(__name__)

_DEFAULTS = {
    "coins_per_pound": 4800.0,
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


def load_encumbrance_cfg(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        log.warning("encumbrance_loader: Lua engine unavailable - using defaults")
        return _merge_defaults(_DEFAULTS, {})

    try:
        data = lua_engine.load_data("globals/encumbrance")
        if not data:
            log.warning("encumbrance_loader: Lua returned no data - using defaults")
            return _merge_defaults(_DEFAULTS, {})
        cfg = _merge_defaults(_DEFAULTS, data)
        log.info("encumbrance_loader: loaded encumbrance config from Lua")
        return cfg
    except Exception as e:
        log.warning("encumbrance_loader: failed to load Lua config (%s) - using defaults", e)
        return _merge_defaults(_DEFAULTS, {})
