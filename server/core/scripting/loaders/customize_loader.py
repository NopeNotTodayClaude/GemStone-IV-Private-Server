"""
customize_loader.py
-------------------
Loads customize/order configuration from scripts/globals/customize.lua.
"""

import logging

log = logging.getLogger(__name__)

_DEFAULTS = {
    "order_wait": {
        "min_seconds": 0,
        "max_seconds": 60,
        "no_material_seconds": 0,
        "default_material_seconds": 10,
        "instant_materials": {
            "iron": True,
            "steel": True,
            "bronze": True,
        },
        "material_seconds": {
            "silver": 5,
            "gold": 5,
            "invar": 10,
            "mithril": 15,
            "ora": 20,
            "imflass": 25,
            "laje": 28,
            "carmiln": 30,
            "faenor": 34,
            "gornar": 36,
            "rhimar": 38,
            "zorchar": 40,
            "drakar": 42,
            "razern": 44,
            "vaalorn": 46,
            "glaes": 48,
            "mithglin": 50,
            "veniom": 50,
            "eahnor": 52,
            "vultite": 54,
            "rolaren": 55,
            "eonake": 56,
            "kelyn": 57,
            "urglaes": 58,
            "golvern": 59,
            "krodera": 60,
            "kroderine": 60,
            "coraesine": 60,
        },
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


def load_customize_cfg(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        log.warning("customize_loader: Lua engine unavailable - using defaults")
        return _merge_defaults(_DEFAULTS, {})

    try:
        data = lua_engine.load_data("globals/customize")
        if not data:
            log.warning("customize_loader: Lua returned no data - using defaults")
            return _merge_defaults(_DEFAULTS, {})
        cfg = _merge_defaults(_DEFAULTS, data)
        log.info("customize_loader: loaded customize config from Lua")
        return cfg
    except Exception as e:
        log.warning("customize_loader: failed to load Lua config (%s) - using defaults", e)
        return _merge_defaults(_DEFAULTS, {})
