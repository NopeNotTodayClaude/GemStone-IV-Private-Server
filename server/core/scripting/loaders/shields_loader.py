"""
shields_loader.py
-----------------
Loads shield template data from scripts/data/items/shields.lua.

Returns a list of dicts matching the format expected by the DB seeder.
Returns None if Lua is unavailable or the file fails to load.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def load_shields(lua_engine) -> Optional[list]:
    """
    Returns a list of shield template dicts, or None on failure.
    """
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("shields_loader: Lua engine not available — cannot load data")
    try:
        data = lua_engine.load_data("data/items/shields")
        if not data:
            raise RuntimeError("shields_loader: Lua returned no data — check scripts/data/ for errors")
        raw = data.get("templates") or []
        if not isinstance(raw, list):
            raise RuntimeError("shields_loader: unexpected None from Lua loader")
        result = [_normalise_shield(s) for s in raw if isinstance(s, dict)]
        log.info("shields_loader: loaded %d shield templates from Lua", len(result))
        return result
    except Exception as e:
        log.warning("shields_loader: failed: %s", e)
        raise RuntimeError("shields_loader: unexpected None from Lua loader")


def _normalise_shield(raw: dict) -> dict:
    return {
        "base_name":         str(raw.get("base_name", "")),
        "name":              str(raw.get("name", "")),
        "short_name":        str(raw.get("short_name", raw.get("name", ""))),
        "noun":              str(raw.get("noun", "shield")),
        "item_type":         "shield",
        "shield_type":       str(raw.get("shield_type", "medium")),
        "weight":            float(raw.get("weight", 8.0)),
        "shield_ds":         int(raw.get("shield_ds", 20)),
        "shield_evade_pen":  int(raw.get("shield_evade_pen", 30)),
        "shield_size_mod":   int(raw.get("shield_size_mod", 0)),
        "value":             int(raw.get("value", 0)),
        "material":          str(raw.get("material", "steel")),
        "description":       str(raw.get("description", "")),
    }
