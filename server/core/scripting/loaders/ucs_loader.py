"""
ucs_loader.py
-------------
Loads scripts/globals/ucs.lua and updates the shared UCS runtime config.
"""

import logging

from server.core.engine.combat.ucs_runtime import configure_ucs, get_ucs_cfg

log = logging.getLogger(__name__)


def load_ucs_cfg(lua_engine) -> dict:
    """
    Load UCS config from Lua and push it into the shared runtime cache.
    Falls back to runtime defaults if Lua is unavailable or invalid.
    """
    if not lua_engine or not lua_engine.available:
        log.warning("ucs_loader: Lua engine unavailable — using defaults")
        return configure_ucs(None)

    try:
        data = lua_engine.load_data("globals/ucs")
        if not isinstance(data, dict):
            log.warning("ucs_loader: Lua returned no data — using defaults")
            return configure_ucs(None)
        cfg = configure_ucs(data)
        log.info("ucs_loader: loaded UCS config from Lua")
        return cfg
    except Exception as exc:
        log.warning("ucs_loader: failed to load Lua config (%s) — using defaults", exc)
        return configure_ucs(None)
