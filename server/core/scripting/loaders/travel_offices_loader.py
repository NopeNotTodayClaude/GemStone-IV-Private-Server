"""
travel_offices_loader.py
------------------------
Loads scripts/data/travel_offices.lua into a normalized Python dict.
"""

import logging

log = logging.getLogger(__name__)


def _to_int(value, default=0):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return int(default)


def _to_list(values):
    if isinstance(values, (list, tuple)):
        return [str(v).strip() for v in values if str(v).strip()]
    if values is None:
        return []
    text = str(values).strip()
    return [text] if text else []


def load_travel_offices(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        log.warning("travel_offices_loader: Lua engine unavailable")
        return {"networks": {}, "offices": {}}

    try:
        data = lua_engine.load_data("data/travel_offices") or {}
        if not isinstance(data, dict):
            log.warning("travel_offices_loader: travel_offices.lua returned non-dict data")
            return {"networks": {}, "offices": {}}

        networks_raw = data.get("networks") or {}
        offices_raw = data.get("offices") or {}
        networks = {}
        offices = {}

        for network_id, raw in networks_raw.items():
            if not isinstance(raw, dict):
                continue
            nid = str(network_id or "").strip().lower()
            if not nid:
                continue
            networks[nid] = {
                "id": nid,
                "service": str(raw.get("service") or nid).strip().lower(),
                "display_name": str(raw.get("display_name") or nid).strip(),
                "max_level": _to_int(raw.get("max_level"), 0),
                "standard_fare": max(0, _to_int(raw.get("standard_fare"), 0)),
                "ticket_fare": max(0, _to_int(raw.get("ticket_fare"), 0)),
                "day_pass_fare": max(0, _to_int(raw.get("day_pass_fare"), 0)),
                "pass_duration_sec": max(0, _to_int(raw.get("pass_duration_sec"), 0)),
                "departure_interval_sec": max(0, _to_int(raw.get("departure_interval_sec"), 0)),
                "roundtime_sec": max(0, _to_int(raw.get("roundtime_sec"), 0)),
                "route_group": str(raw.get("route_group") or "").strip().lower(),
                "free_use_unlock": str(raw.get("free_use_unlock") or "").strip().lower(),
                "depart_msg": str(raw.get("depart_msg") or "").strip(),
                "arrive_msg": str(raw.get("arrive_msg") or "").strip(),
            }

        for office_id, raw in offices_raw.items():
            if not isinstance(raw, dict):
                continue
            oid = str(office_id or "").strip().lower()
            if not oid:
                continue
            room_id = _to_int(raw.get("room_id"), 0)
            if room_id <= 0:
                continue
            offices[oid] = {
                "id": oid,
                "network": str(raw.get("network") or "").strip().lower(),
                "town_name": str(raw.get("town_name") or "").strip(),
                "room_id": room_id,
                "departure_room_id": _to_int(raw.get("departure_room_id"), room_id) or room_id,
                "arrival_room_id": _to_int(raw.get("arrival_room_id"), room_id) or room_id,
                "clerk_template_id": str(raw.get("clerk_template_id") or "").strip(),
                "clerk_label": str(raw.get("clerk_label") or "").strip(),
                "route_group": str(raw.get("route_group") or "").strip().lower(),
                "aliases": [alias.lower() for alias in _to_list(raw.get("aliases"))],
            }

        log.info(
            "travel_offices_loader: loaded %d office definitions across %d networks",
            len(offices),
            len(networks),
        )
        return {"networks": networks, "offices": offices}

    except Exception as e:
        log.error("travel_offices_loader: failed to load travel offices (%s)", e, exc_info=True)
        return {"networks": {}, "offices": {}}
