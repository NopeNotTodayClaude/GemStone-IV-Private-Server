"""
containers_loader.py
--------------------
Loads container data from scripts/data/items/containers.lua.

Returns a dict with keys:
  "wearable"  - list of wearable container template dicts
  "treasure"  - list of treasure (locked box) template dicts

Returns None on failure.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def load_containers(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("containers_loader: Lua engine not available — cannot load data")
    try:
        data = lua_engine.load_data("data/items/containers")
        if not data:
            raise RuntimeError("containers_loader: Lua returned no data — check scripts/data/ for errors")

        wearable = data.get("wearable") or []
        treasure = data.get("treasure") or []

        result = {
            "wearable": [_normalise_container(c) for c in wearable if isinstance(c, dict)],
            "treasure": [_normalise_container(c) for c in treasure if isinstance(c, dict)],
        }
        total = len(result["wearable"]) + len(result["treasure"])
        log.info("containers_loader: loaded %d containers (%d wearable, %d treasure)",
                 total, len(result["wearable"]), len(result["treasure"]))
        return result
    except Exception as e:
        log.warning("containers_loader: failed: %s", e)
        raise RuntimeError("containers_loader: unexpected None from Lua loader")


def _normalise_container(raw: dict) -> dict:
    return {
        "base_name":       str(raw.get("base_name", "")),
        "name":            str(raw.get("name", "")),
        "short_name":      str(raw.get("short_name", raw.get("name", ""))),
        "noun":            str(raw.get("noun", "container")),
        "item_type":       "container",
        "container_type":  str(raw.get("container_type", "wearable")),
        "capacity":        int(raw.get("capacity", 20)),
        "worn_location":   raw.get("worn_location"),  # None for treasure containers
        "weight":          float(raw.get("weight", 1.0)),
        "value":           int(raw.get("value", 0)),
        "lock_difficulty": int(raw.get("lock_difficulty", 0)),
        "trap_type":       raw.get("trap_type"),  # None if no trap
        "description":     str(raw.get("description", raw.get("name", ""))),
    }
