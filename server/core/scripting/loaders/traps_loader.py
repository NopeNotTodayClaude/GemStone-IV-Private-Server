"""
traps_loader.py
---------------
Loads scripts/data/traps.lua for the LuaManager cache.
"""

import logging

log = logging.getLogger(__name__)


def load_traps(engine) -> dict:
    """Load scripts/data/traps.lua and return a Python dict."""
    if not engine or not engine.available:
        return None
    try:
        data = engine.load_data("data/traps")
        if isinstance(data, dict) and data:
            log.info("traps_loader: loaded trap system data")
            return data
        log.warning("traps_loader: empty or invalid data returned from Lua")
        return None
    except Exception as e:
        log.error("traps_loader: failed to load traps.lua: %s", e, exc_info=True)
        return None
