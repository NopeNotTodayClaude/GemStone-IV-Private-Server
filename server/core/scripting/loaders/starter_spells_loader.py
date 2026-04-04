"""
starter_spells_loader.py
------------------------
Loads starter spell definitions from scripts/data/starter_spells.lua.

Returns a dict:
  "kits" - {prof_id: {"description": str, "ranks": {circle_id: known_count}}}
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def _iter_numeric_mapping(raw):
    if isinstance(raw, dict):
        for k, v in raw.items():
            try:
                yield int(k), v
            except Exception:
                continue
        return
    if isinstance(raw, list):
        for idx, value in enumerate(raw, 1):
            if value is None:
                continue
            yield idx, value


def load_starter_spells(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("starter_spells_loader: Lua engine not available. Check lupa installation and scripts path.")
    try:
        data = lua_engine.load_data("data/starter_spells")
        if not data:
            raise RuntimeError("starter_spells_loader: Lua returned no data. Check scripts/data/starter_spells.lua.")

        kits = {}
        for prof_id, raw_kit in _iter_numeric_mapping(data.get("kits") or {}):
            if not isinstance(raw_kit, dict):
                continue
            ranks = {}
            for circle_id, rank_count in _iter_numeric_mapping(raw_kit.get("ranks") or {}):
                ranks[int(circle_id)] = max(0, int(rank_count or 0))
            kits[int(prof_id)] = {
                "description": str(raw_kit.get("description") or ""),
                "ranks": ranks,
            }

        log.info("starter_spells_loader: loaded %d profession spell kits from Lua", len(kits))
        return {"kits": kits}
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("starter_spells_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"starter_spells_loader: Lua load failed — {e}") from e
