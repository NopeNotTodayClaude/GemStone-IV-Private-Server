"""
spell_hotbar_loader.py
----------------------
Loads scripts/data/spell_hotbar.lua for Lua-driven spell hotbar execution data.
"""

import logging

log = logging.getLogger(__name__)


def load_spell_hotbar(engine) -> dict:
    """Load scripts/data/spell_hotbar.lua and return a Python dict."""
    if not engine or not engine.available:
        return None
    try:
        data = engine.load_data("data/spell_hotbar")
        if isinstance(data, dict):
            log.info("spell_hotbar_loader: loaded spell hotbar data")
            return data
        log.warning("spell_hotbar_loader: empty or invalid data returned from Lua")
        return None
    except Exception as e:
        log.error("spell_hotbar_loader: failed to load spell_hotbar.lua: %s", e, exc_info=True)
        return None
