"""
races_loader.py
---------------
Loads race definitions from scripts/data/races.lua into the structures
that character_creation.py expects.

Returns a dict with keys:
  "races"            - list of {id, name, desc}
  "stat_mods"        - {race_id: [STR,CON,DEX,AGI,DIS,AUR,LOG,INT,WIS,INF]}
  "growth_mods"      - {race_id: [STR,...]}
  "starting_rooms"   - {race_id: room_id}
  "town_names"       - {room_id: name}
  "starter_towns"    - list of {room_id, name}
  "default_starting_room" - int room_id

Returns None if Lua is unavailable or the file fails to load.
Raises RuntimeError if Lua unavailable or the file fails to load.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def _iter_numeric_mapping(raw):
    """Yield (1-based numeric key, value) pairs from either dict or list data."""
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


def _load_numeric_list_map(raw):
    out = {}
    for key, value in _iter_numeric_mapping(raw):
        if isinstance(value, list):
            out[int(key)] = [int(x) for x in value]
    return out


def _load_numeric_scalar_map(raw, *, value_cast=int):
    out = {}
    for key, value in _iter_numeric_mapping(raw):
        try:
            out[int(key)] = value_cast(value)
        except Exception:
            continue
    return out


def load_races(lua_engine) -> Optional[dict]:
    """Try to load races from Lua.  Returns None on any failure."""
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("races_loader: Lua engine not available. Check lupa installation and scripts path.")
    try:
        data = lua_engine.load_data("data/races")
        if not data:
            raise RuntimeError("races_loader: Lua returned no data. Check scripts/data/ for errors.")

        races       = []
        stat_mods   = {}
        growth_mods = {}
        start_rooms = {}
        town_names  = {}
        starter_towns = []
        default_starting_room = 221

        # data["list"] is a list of race tables
        for r in (data.get("list") or []):
            if not isinstance(r, dict):
                continue
            races.append({
                "id":   int(r.get("id", 0)),
                "name": str(r.get("name", "")),
                "desc": str(r.get("desc", "")),
            })

        # Numeric-keyed Lua tables may arrive as dicts or dense lists depending on
        # the runtime bridge. Accept both shapes.
        stat_mods = _load_numeric_list_map(data.get("stat_mods") or {})

        growth_mods = _load_numeric_list_map(data.get("growth_mods") or {})

        start_rooms = _load_numeric_scalar_map(data.get("starting_rooms") or {}, value_cast=int)

        town_names = _load_numeric_scalar_map(data.get("town_names") or {}, value_cast=str)

        for row in (data.get("starter_towns") or []):
            if not isinstance(row, dict):
                continue
            room_id = int(row.get("room_id", 0) or 0)
            name = str(row.get("name", "") or "")
            if room_id > 0 and name:
                starter_towns.append({
                    "room_id": room_id,
                    "name": name,
                })

        default_starting_room = int(data.get("default_starting_room") or default_starting_room)

        log.info("races_loader: loaded %d races from Lua", len(races))
        return {
            "races":          races,
            "stat_mods":      stat_mods,
            "growth_mods":    growth_mods,
            "starting_rooms": start_rooms,
            "town_names":     town_names,
            "starter_towns":  starter_towns,
            "default_starting_room": default_starting_room,
        }
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("races_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"races_loader: Lua load failed — {e}") from e
