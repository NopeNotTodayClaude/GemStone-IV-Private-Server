"""
starter_gear_loader.py
----------------------
Loads starter gear definitions from scripts/data/starter_gear.lua.

Returns a dict with keys:
  "starting_silver"  - {prof_id: amount}
  "kits"             - {prof_id: {"description": str, "items": [...]}}

Raises RuntimeError if Lua unavailable or load fails.
Raises RuntimeError if Lua unavailable or load fails.
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


def load_starter_gear(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("starter_gear_loader: Lua engine not available. Check lupa installation and scripts path.")
    try:
        data = lua_engine.load_data("data/starter_gear")
        if not data:
            raise RuntimeError("starter_gear_loader: Lua returned no data. Check scripts/data/ for errors.")

        silver = {}
        for k, v in _iter_numeric_mapping(data.get("starting_silver") or {}):
            silver[int(k)] = int(v)

        kits = {}
        for k, v in _iter_numeric_mapping(data.get("kits") or {}):
            if not isinstance(v, dict):
                continue
            prof_id = int(k)
            items = []
            for item in (v.get("items") or []):
                if isinstance(item, dict):
                    entry = {}
                    for ik, iv in item.items():
                        entry[str(ik)] = iv
                    # Normalise numeric fields
                    if "item_id" in entry:
                        entry["item_id"] = int(entry["item_id"])
                    items.append(entry)
            kits[prof_id] = {
                "description": str(v.get("description", "")),
                "items": items,
            }

        log.info("starter_gear_loader: loaded %d profession kits from Lua", len(kits))
        return {
            "starting_silver": silver,
            "kits": kits,
        }
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("starter_gear_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"starter_gear_loader: Lua load failed — {e}") from e
