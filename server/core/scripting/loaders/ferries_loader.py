"""
ferries_loader.py
-----------------
Loads ferry route definitions from scripts/data/ferries.lua.

The Lua file is the source of truth for ferry topology, timing, fares,
and room-facing messaging.  The Python runtime only normalizes the data
into a stable dict for FerryManager.
"""

import logging

log = logging.getLogger(__name__)


def load_ferries(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        log.warning("ferries_loader: Lua engine unavailable")
        return {}

    try:
        data = lua_engine.load_data("data/ferries") or {}
        if not isinstance(data, dict):
            log.warning("ferries_loader: ferries.lua returned non-dict data")
            return {}

        result = {}
        for ferry_id, raw in data.items():
            if not isinstance(raw, dict):
                continue

            sides = {}
            for side_name, side_raw in (raw.get("sides") or {}).items():
                if not isinstance(side_raw, dict):
                    continue
                try:
                    room_id = int(side_raw.get("room_id") or 0)
                except (TypeError, ValueError):
                    room_id = 0
                if room_id <= 0:
                    continue
                try:
                    fare = int(side_raw.get("fare") or 0)
                except (TypeError, ValueError):
                    fare = 0
                sides[str(side_name).lower()] = {
                    "room_id": room_id,
                    "fare": max(0, fare),
                    "entity_line": str(side_raw.get("entity_line") or ""),
                    "ferryman_line": str(side_raw.get("ferryman_line") or ""),
                    "board_msg": str(side_raw.get("board_msg") or ""),
                    "deny_msg": str(side_raw.get("deny_msg") or ""),
                    "departure_room_msg": str(side_raw.get("departure_room_msg") or ""),
                    "arrival_room_msg": str(side_raw.get("arrival_room_msg") or ""),
                }

            if len(sides) < 2:
                continue

            onboard_room_ids = []
            for rid in raw.get("onboard_room_ids") or []:
                try:
                    onboard_room_ids.append(int(rid))
                except (TypeError, ValueError):
                    continue

            try:
                ferry_room_id = int(raw.get("ferry_room_id") or 0)
            except (TypeError, ValueError):
                ferry_room_id = 0
            if ferry_room_id <= 0:
                continue

            if ferry_room_id not in onboard_room_ids:
                onboard_room_ids.insert(0, ferry_room_id)

            try:
                dock_duration_sec = int(raw.get("dock_duration_sec") or 60)
            except (TypeError, ValueError):
                dock_duration_sec = 60
            try:
                travel_duration_sec = int(raw.get("travel_duration_sec") or 60)
            except (TypeError, ValueError):
                travel_duration_sec = 60

            result[str(ferry_id)] = {
                "id": str(raw.get("id") or ferry_id),
                "name": str(raw.get("name") or ferry_id),
                "ferry_room_id": ferry_room_id,
                "onboard_room_ids": onboard_room_ids,
                "boarding_exit": str(raw.get("boarding_exit") or "go_plank"),
                "dock_duration_sec": max(5, dock_duration_sec),
                "travel_duration_sec": max(5, travel_duration_sec),
                "start_side": str(raw.get("start_side") or next(iter(sides.keys()))).lower(),
                "ferry_look": str(raw.get("ferry_look") or ""),
                "ferryman_look": str(raw.get("ferryman_look") or ""),
                "onboard_depart_msg": str(raw.get("onboard_depart_msg") or ""),
                "onboard_arrive_msg": str(raw.get("onboard_arrive_msg") or ""),
                "sides": sides,
            }

        log.info("ferries_loader: loaded %d ferry routes from Lua", len(result))
        return result

    except Exception as e:
        log.error("ferries_loader: failed to load ferries (%s)", e, exc_info=True)
        return {}
