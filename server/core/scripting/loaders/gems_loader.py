"""
gems_loader.py
--------------
Loads gem data from scripts/data/items/gems.lua.

Returns a list of gem template dicts, or None on failure.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def load_gems(lua_engine) -> Optional[list]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("gems_loader: Lua engine not available — cannot load data")
    try:
        data = lua_engine.load_data("data/items/gems")
        if not data:
            raise RuntimeError("gems_loader: Lua returned no data — check scripts/data/ for errors")
        raw = data.get("list") or []
        if not isinstance(raw, list):
            raise RuntimeError("gems_loader: unexpected None from Lua loader")
        result = [_normalise_gem(g) for g in raw if isinstance(g, dict)]
        log.info("gems_loader: loaded %d gem templates from Lua", len(result))
        return result
    except Exception as e:
        log.warning("gems_loader: failed: %s", e)
        raise RuntimeError("gems_loader: unexpected None from Lua loader")


def _normalise_gem(raw: dict) -> dict:
    return {
        "name":        str(raw.get("name", "")),
        "noun":        str(raw.get("noun", "gem")),
        "item_type":   "gem",
        "gem_family":  str(raw.get("gem_family", "misc")),
        "value":       int(raw.get("value", 0)),
        "weight":      int(raw.get("weight", 1)),
        "region":      str(raw.get("region", "any")),
        "description": str(raw.get("description", raw.get("name", ""))),
    }
