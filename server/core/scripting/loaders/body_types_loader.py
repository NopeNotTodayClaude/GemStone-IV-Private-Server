"""
body_types_loader.py
Loads scripts/data/body_types.lua into a Python dict keyed by body_type string.

Result structure:
  BODY_TYPES["biped"] = {
    "locations": {
      "head":      {"weight": 5,  "aim_penalty": 15, "label": "head"},
      "chest":     {"weight": 20, "aim_penalty": 0,  "label": "chest"},
      ...
    },
    "aimable": ["head", "neck", "chest", ...],
  }

Usage:
  from server.core.scripting.loaders.body_types_loader import BODY_TYPES, get_locations, get_aimable

  locs    = get_locations("quadruped")     # dict of location → {weight, aim_penalty, label}
  aimable = get_aimable("ophidian")        # list of valid AIM target strings
"""

import os
import logging
from lupa import LuaRuntime  # type: ignore

log = logging.getLogger(__name__)

# Resolved once at module import — walk up from this file to the project root
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
_LUA_FILE = os.path.join(_PROJECT_ROOT, "scripts", "data", "body_types.lua")

BODY_TYPES: dict = {}


def _lua_table_to_dict(tbl):
    """Recursively convert a lupa LuaTable to a plain Python dict/list."""
    if tbl is None:
        return None
    result = {}
    for k, v in tbl.items():
        if hasattr(v, "items"):
            # Nested table — could be dict-like or array-like
            # Check if keys are sequential integers → list
            items = list(v.items())
            if items and all(isinstance(k2, int) for k2, _ in items):
                result[k] = [v2 for _, v2 in sorted(items)]
            else:
                result[k] = _lua_table_to_dict(v)
        else:
            result[k] = v
    return result


def _load_body_types() -> dict:
    """Parse body_types.lua and return a Python dict."""
    if not os.path.isfile(_LUA_FILE):
        raise RuntimeError(
            f"body_types_loader: body_types.lua not found at {_LUA_FILE}. "
            "Check your scripts path configuration."
        )

    try:
        lua = LuaRuntime(unpack_returned_tuples=True)
        with open(_LUA_FILE, "r", encoding="utf-8") as f:
            src = f.read()
        result_table = lua.execute(src)
        raw = _lua_table_to_dict(result_table)

        parsed = {}
        for body_type, data in raw.items():
            if not isinstance(data, dict):
                continue
            locs_raw = data.get("locations", {})
            aim_raw  = data.get("aimable", {})

            # locations: dict of name → {weight, aim_penalty, label}
            locations = {}
            for loc_name, loc_data in locs_raw.items():
                if isinstance(loc_data, dict):
                    locations[loc_name] = {
                        "weight":      int(loc_data.get("weight",      10)),
                        "aim_penalty": int(loc_data.get("aim_penalty", 10)),
                        "label":       str(loc_data.get("label",       loc_name)),
                    }

            # aimable: list of location strings
            if isinstance(aim_raw, list):
                aimable = [str(x) for x in aim_raw]
            elif isinstance(aim_raw, dict):
                aimable = [str(v) for _, v in sorted(aim_raw.items())]
            else:
                aimable = list(locations.keys())

            parsed[body_type] = {
                "locations": locations,
                "aimable":   aimable,
            }

        log.info("body_types_loader: loaded %d body types", len(parsed))
        return parsed

    except Exception as e:
        log.critical("body_types_loader: failed to load %s: %s", _LUA_FILE, e, exc_info=True)
        raise RuntimeError(f"body_types_loader: failed to load body_types.lua — {e}") from e


# Load once at import time
BODY_TYPES = _load_body_types()

# ── Public helpers ────────────────────────────────────────────────────────────

def get_locations(body_type: str) -> dict:
    """
    Return the locations dict for a given body_type.
    Falls back to "biped" if the type is unknown (all creatures have at least biped).
    Raises if body_types.lua never loaded.
    """
    if not BODY_TYPES:
        raise RuntimeError(
            "body_types_loader: BODY_TYPES is empty — "
            "body_types.lua failed to load at startup"
        )
    bt = BODY_TYPES.get(body_type) or BODY_TYPES.get("biped") or {}
    return bt.get("locations", {})


def get_aimable(body_type: str) -> list:
    """
    Return the list of valid AIM location strings for a body_type.
    Raises if body_types.lua never loaded.
    """
    if not BODY_TYPES:
        raise RuntimeError(
            "body_types_loader: BODY_TYPES is empty — "
            "body_types.lua failed to load at startup"
        )
    bt = BODY_TYPES.get(body_type) or BODY_TYPES.get("biped") or {}
    return bt.get("aimable", [])


def get_location_label(body_type: str, location: str) -> str:
    """
    Return the display label for a location on a creature of the given body type.
    e.g. get_location_label("quadruped", "right flank") -> "right flank"
    """
    locs = get_locations(body_type)
    return locs.get(location, {}).get("label", location)


def random_location(body_type: str) -> str:
    """
    Pick a weighted-random hit location for a given body_type.
    """
    import random
    locs = get_locations(body_type)
    if not locs:
        return "chest"
    names   = list(locs.keys())
    weights = [locs[n]["weight"] for n in names]
    return random.choices(names, weights=weights, k=1)[0]


def resolve_aim(body_type: str, requested: str) -> str | None:
    """
    Resolve a player's AIM input (case-insensitive) to a canonical location key.
    Returns None if the location doesn't exist on this body type.

    Examples:
      resolve_aim("biped", "HEAD")        -> "head"
      resolve_aim("biped", "right arm")   -> "right arm"
      resolve_aim("quadruped", "head")    -> "head"
      resolve_aim("quadruped", "right hand") -> None  (quadrupeds have no hand)
    """
    locs    = get_locations(body_type)
    aimable = get_aimable(body_type)
    req     = requested.strip().lower()
    # Exact match first
    if req in locs and req in aimable:
        return req
    # Partial match against aimable labels
    for loc in aimable:
        if loc.startswith(req) or req in loc:
            return loc
    return None


