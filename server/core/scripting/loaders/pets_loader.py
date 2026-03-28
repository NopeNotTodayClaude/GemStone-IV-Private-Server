"""
pets_loader.py
--------------
Loads scripts/data/pets.lua for the LuaManager cache.
"""

import logging

log = logging.getLogger(__name__)


def load_pets(engine) -> dict:
    """Load scripts/data/pets.lua and return a Python dict."""
    if not engine or not engine.available:
        return None
    try:
        data = engine.load_data("data/pets")
        if isinstance(data, dict) and data:
            log.info("pets_loader: loaded pet system data")
            return data
        log.warning("pets_loader: empty or invalid data returned from Lua")
        return None
    except Exception as e:
        log.error("pets_loader: failed to load pets.lua: %s", e, exc_info=True)
        return None
