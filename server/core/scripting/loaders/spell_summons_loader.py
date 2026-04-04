"""
spell_summons_loader.py
-----------------------
Loads scripts/data/spell_summons.lua for summoned-spell runtime metadata.
"""

import logging

log = logging.getLogger(__name__)


def load_spell_summons(engine) -> dict:
    """Load scripts/data/spell_summons.lua and return a Python dict."""
    if not engine or not engine.available:
        return None
    try:
        data = engine.load_data("data/spell_summons")
        if isinstance(data, dict) and data:
            log.info("spell_summons_loader: loaded spell summon data")
            return data
        log.warning("spell_summons_loader: empty or invalid data returned from Lua")
        return None
    except Exception as e:
        log.error("spell_summons_loader: failed to load spell_summons.lua: %s", e, exc_info=True)
        return None

