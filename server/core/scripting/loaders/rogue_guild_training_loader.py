"""Load rogue guild trainer curriculum from Lua."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def load_rogue_guild_training(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        return {}
    try:
        data = lua_engine.load_data("data/rogue_guild_training")
        return data if isinstance(data, dict) else {}
    except Exception as e:
        log.warning("rogue_guild_training_loader: failed: %s", e)
        return {}
