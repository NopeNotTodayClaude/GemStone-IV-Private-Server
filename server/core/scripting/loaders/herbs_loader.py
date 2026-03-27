"""
herbs_loader.py
---------------
Loads herb data from scripts/data/items/herbs.lua.

Returns a list of herb template dicts, or None on failure.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def load_herbs(lua_engine) -> Optional[list]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("herbs_loader: Lua engine not available — cannot load data")
    try:
        data = lua_engine.load_data("data/items/herbs")
        if not data:
            raise RuntimeError("herbs_loader: Lua returned no data — check scripts/data/ for errors")
        raw = data.get("list") or []
        if not isinstance(raw, list):
            raise RuntimeError("herbs_loader: unexpected None from Lua loader")
        result = [_normalise_herb(h) for h in raw if isinstance(h, dict)]
        log.info("herbs_loader: loaded %d herb templates from Lua", len(result))
        return result
    except Exception as e:
        log.warning("herbs_loader: failed: %s", e)
        raise RuntimeError("herbs_loader: unexpected None from Lua loader")


def _normalise_herb(raw: dict) -> dict:
    return {
        "name":          str(raw.get("name", "")),
        "noun":          str(raw.get("noun", "herb")),
        "item_type":     "herb",
        "heal_type":     str(raw.get("heal_type", "blood")),
        "heal_rank":     int(raw.get("heal_rank", 1)),
        "heal_amount":   int(raw.get("heal_amount", 0)),
        "roundtime":     int(raw.get("roundtime", 5)),
        "weight":        int(raw.get("weight", 1)),
        "value":         int(raw.get("value", 0)),
        "description":   str(raw.get("description", raw.get("name", ""))),
        "lore_text":     str(raw.get("lore_text", "")),
    }
