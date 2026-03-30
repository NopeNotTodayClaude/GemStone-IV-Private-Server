"""
hotbar_actions_loader.py
------------------------
Loads scripts/data/hotbar_actions.lua for the LuaManager cache.
"""

import logging

log = logging.getLogger(__name__)


def load_hotbar_actions(engine) -> dict:
    """Load scripts/data/hotbar_actions.lua and return a Python dict."""
    if not engine or not engine.available:
        return None
    try:
        data = engine.load_data("data/hotbar_actions")
        if isinstance(data, dict) and data:
            log.info("hotbar_actions_loader: loaded hotbar action data")
            return data
        log.warning("hotbar_actions_loader: empty or invalid data returned from Lua")
        return None
    except Exception as e:
        log.error("hotbar_actions_loader: failed to load hotbar_actions.lua: %s", e, exc_info=True)
        return None
