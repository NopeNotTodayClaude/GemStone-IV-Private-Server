"""
status_loader.py
----------------
Loads the status_effects.lua data table for the LuaManager cache.
Called by LuaManager.get_status_effects().
"""

import logging

log = logging.getLogger(__name__)


def load_status_effects(engine) -> dict:
    """
    Load scripts/data/status_effects.lua and return a Python dict of defs.
    Returns None if the engine is unavailable or loading fails.
    """
    if not engine or not engine.available:
        return None
    try:
        data = engine.load_data("data/status_effects")
        if isinstance(data, dict) and data:
            log.info("status_loader: loaded %d status effect definitions", len(data))
            return data
        log.warning("status_loader: empty or invalid data returned from Lua")
        return None
    except Exception as e:
        log.error("status_loader: failed to load status_effects.lua: %s", e)
        return None
