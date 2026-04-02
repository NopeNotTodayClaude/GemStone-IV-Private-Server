"""
inns_loader.py
--------------
Loads scripts/data/inns.lua into a normalized Python dict.
"""

import logging

log = logging.getLogger(__name__)


def _to_int(value, default=0):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return int(default)


def _to_str_list(values):
    if isinstance(values, (list, tuple)):
        return [str(v).strip() for v in values if str(v).strip()]
    if values is None:
        return []
    text = str(values).strip()
    return [text] if text else []


def _to_int_list(values):
    items = []
    for raw in _to_str_list(values):
        try:
            item_id = int(raw)
        except (TypeError, ValueError):
            continue
        if item_id > 0 and item_id not in items:
            items.append(item_id)
    return items


def load_inns(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        log.warning("inns_loader: Lua engine unavailable")
        return {"defaults": {}, "inns": {}}

    try:
        data = lua_engine.load_data("data/inns") or {}
        if not isinstance(data, dict):
            log.warning("inns_loader: inns.lua returned non-dict data")
            return {"defaults": {}, "inns": {}}

        defaults_raw = data.get("defaults") or {}
        inns_raw = data.get("inns") or {}
        defaults = {
            "auto_latch_tag": bool(defaults_raw.get("auto_latch_tag", True)),
        }
        inns = {}

        for inn_id, raw in inns_raw.items():
            if not isinstance(raw, dict):
                continue

            normalized_id = str(inn_id or "").strip().lower()
            front_desk_room_id = _to_int(raw.get("front_desk_room_id"), 0)
            if not normalized_id or front_desk_room_id <= 0:
                continue

            explicit_room_ids = _to_int_list(raw.get("explicit_room_ids"))
            rentable_room_ids = _to_int_list(raw.get("rentable_room_ids"))
            private_table_room_ids = _to_int_list(raw.get("private_table_room_ids"))

            for room_id in (front_desk_room_id, *rentable_room_ids, *private_table_room_ids):
                if room_id > 0 and room_id not in explicit_room_ids:
                    explicit_room_ids.append(room_id)

            inns[normalized_id] = {
                "id": normalized_id,
                "display_name": str(raw.get("display_name") or normalized_id).strip(),
                "town_name": str(raw.get("town_name") or "").strip(),
                "front_desk_room_id": front_desk_room_id,
                "aliases": [alias.lower() for alias in _to_str_list(raw.get("aliases"))],
                "room_title_prefixes": _to_str_list(raw.get("room_title_prefixes")),
                "location_names": _to_str_list(raw.get("location_names")),
                "explicit_room_ids": explicit_room_ids,
                "rentable_room_ids": rentable_room_ids,
                "private_table_room_ids": private_table_room_ids,
                "innkeeper_template_ids": _to_str_list(raw.get("innkeeper_template_ids")),
                "auto_latch_tag": bool(raw.get("auto_latch_tag", defaults["auto_latch_tag"])),
            }

        log.info("inns_loader: loaded %d inn definitions", len(inns))
        return {"defaults": defaults, "inns": inns}

    except Exception as e:
        log.error("inns_loader: failed to load inns (%s)", e, exc_info=True)
        return {"defaults": {}, "inns": {}}
