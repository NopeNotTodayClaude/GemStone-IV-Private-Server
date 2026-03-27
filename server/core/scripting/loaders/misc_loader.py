"""
misc_loader.py
--------------
Loads miscellaneous item data from scripts/data/items/misc.lua.

Returns a dict with keys:
  "ores"       - list of ore template dicts
  "runestones" - list of runestone template dicts
  "scrolls"    - list of scroll template dicts
  "ammunition" - list of ammo template dicts
  "food"       - list of food/drink template dicts
  "tools"      - list of tool/instrument/component dicts
  "pawnables"  - list of pawnshop-fodder dicts

Returns None on failure.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)

_CATEGORIES = ("ores", "runestones", "scrolls", "ammunition", "food", "tools", "pawnables")


def load_misc(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("misc_loader: Lua engine not available — cannot load data")
    try:
        data = lua_engine.load_data("data/items/misc")
        if not data:
            raise RuntimeError("misc_loader: Lua returned no data — check scripts/data/ for errors")
        result = {}
        total = 0
        for cat in _CATEGORIES:
            raw = data.get(cat)
            if isinstance(raw, list):
                result[cat] = [_normalise_misc(m, cat) for m in raw if isinstance(m, dict)]
            else:
                result[cat] = []
            total += len(result[cat])
        log.info("misc_loader: loaded %d misc items from Lua", total)
        return result
    except Exception as e:
        log.warning("misc_loader: failed: %s", e)
        raise RuntimeError("misc_loader: unexpected None from Lua loader")


def _normalise_misc(raw: dict, category: str) -> dict:
    item_type = str(raw.get("item_type", category.rstrip("s")))
    return {
        "name":          str(raw.get("name", "")),
        "noun":          str(raw.get("noun", "")),
        "item_type":     item_type,
        "weight":        int(raw.get("weight", 1)),
        "value":         int(raw.get("value", 0)),
        "description":   str(raw.get("description", raw.get("name", ""))),
        # Category-specific fields preserved as-is
        **{k: v for k, v in raw.items()
           if k not in ("name", "noun", "item_type", "weight", "value", "description")},
    }
