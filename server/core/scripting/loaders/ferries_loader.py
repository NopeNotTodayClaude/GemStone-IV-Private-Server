"""
ferries_loader.py
-----------------
Loads ferry route definitions from scripts/data/ferries.lua.

The Lua file is the source of truth for ferry topology, timing, messaging,
audio, and encounter configuration. Python only normalizes the data into
runtime-safe dicts for FerryManager.
"""

import logging

log = logging.getLogger(__name__)


def _as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_str(value, default=""):
    return str(value or default)


def _as_int_list(values):
    out = []
    seen = set()
    for value in values or []:
        try:
            ivalue = int(value)
        except (TypeError, ValueError):
            continue
        if ivalue in seen:
            continue
        seen.add(ivalue)
        out.append(ivalue)
    return out


def _normalize_room_transition_mapping(mapping_raw):
    normalized_mapping = {}
    if isinstance(mapping_raw, dict):
        items = mapping_raw.items()
    elif isinstance(mapping_raw, list):
        items = enumerate(mapping_raw, start=1)
    else:
        items = ()

    for src, dest in items:
        src_id = _as_int(src, 0)
        dest_id = _as_int(dest, 0)
        if src_id > 0 and dest_id > 0:
            normalized_mapping[src_id] = dest_id
    return normalized_mapping


def _fallback_room_transitions(onboard_room_ids, underway_room_ids):
    underway = {}
    docked = {}
    pairs = zip(onboard_room_ids or [], underway_room_ids or [])
    for docked_room_id, underway_room_id in pairs:
        docked_room_id = _as_int(docked_room_id, 0)
        underway_room_id = _as_int(underway_room_id, 0)
        if docked_room_id <= 0 or underway_room_id <= 0:
            continue
        underway[docked_room_id] = underway_room_id
        docked[underway_room_id] = docked_room_id
    return {"underway": underway, "docked": docked}


def _normalize_side(side_raw):
    if not isinstance(side_raw, dict):
        return None
    room_id = _as_int(side_raw.get("room_id") or 0)
    if room_id <= 0:
        return None
    return {
        "room_id": room_id,
        "fare": max(0, _as_int(side_raw.get("fare") or 0)),
        "entity_line": _as_str(side_raw.get("entity_line")),
        "ferryman_line": _as_str(side_raw.get("ferryman_line")),
        "board_msg": _as_str(side_raw.get("board_msg")),
        "deny_msg": _as_str(side_raw.get("deny_msg")),
        "departure_room_msg": _as_str(side_raw.get("departure_room_msg")),
        "arrival_room_msg": _as_str(side_raw.get("arrival_room_msg")),
    }


def _normalize_countdown_lines(entries):
    rows = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        seconds = _as_int(entry.get("seconds") or 0)
        line = _as_str(entry.get("line"))
        if seconds <= 0 or not line:
            continue
        rows.append({
            "seconds": seconds,
            "line": line,
        })
    rows.sort(key=lambda row: row["seconds"], reverse=True)
    return rows


def _normalize_variant(variant_id, raw):
    if not isinstance(raw, dict):
        return None
    base_template_id = _as_str(raw.get("base_template_id"))
    name = _as_str(raw.get("name"))
    if not base_template_id or not name:
        return None
    treasure_raw = raw.get("treasure") or {}
    if not isinstance(treasure_raw, dict):
        treasure_raw = {}
    return {
        "key": _as_str(raw.get("key") or variant_id),
        "base_template_id": base_template_id,
        "name": name,
        "article": _as_str(raw.get("article") or "a"),
        "description": _as_str(raw.get("description")),
        "level_offset": _as_int(raw.get("level_offset") or 0),
        "hp_mult": float(raw.get("hp_mult") or 1.0),
        "hp_bonus": _as_int(raw.get("hp_bonus") or 0),
        "as_mult": float(raw.get("as_mult") or 1.0),
        "as_bonus": _as_int(raw.get("as_bonus") or 0),
        "ds_mult": float(raw.get("ds_mult") or 1.0),
        "ds_bonus": _as_int(raw.get("ds_bonus") or 0),
        "td_mult": float(raw.get("td_mult") or 1.0),
        "td_bonus": _as_int(raw.get("td_bonus") or 0),
        "treasure": {
            "coins": bool(treasure_raw.get("coins", False)),
            "gems": bool(treasure_raw.get("gems", False)),
            "magic": bool(treasure_raw.get("magic", False)),
            "boxes": bool(treasure_raw.get("boxes", False)),
        },
    }


def _normalize_wave(entry):
    if not isinstance(entry, dict):
        return None
    variant_id = _as_str(entry.get("variant_id"))
    key = _as_str(entry.get("key"))
    if not variant_id or not key:
        return None
    adds = []
    for add in entry.get("adds") or []:
        if not isinstance(add, dict):
            continue
        add_variant = _as_str(add.get("variant_id"))
        add_count = max(0, _as_int(add.get("count") or 0))
        if add_variant and add_count > 0:
            adds.append({"variant_id": add_variant, "count": add_count})
    hat_drop_raw = entry.get("hat_drop") or {}
    if not isinstance(hat_drop_raw, dict):
        hat_drop_raw = {}
    extra_data = hat_drop_raw.get("extra_data") or {}
    if not isinstance(extra_data, dict):
        extra_data = {}
    return {
        "key": key,
        "label": _as_str(entry.get("label") or key),
        "variant_id": variant_id,
        "fixed_count": max(0, _as_int(entry.get("fixed_count") or 0)),
        "per_player": max(0, _as_int(entry.get("per_player") or 0)),
        "boss": bool(entry.get("boss", False)),
        "adds": adds,
        "hat_drop": {
            "enabled": bool(hat_drop_raw.get("enabled", False)),
            "item_name": _as_str(hat_drop_raw.get("item_name")),
            "chance_pct": max(0, min(100, _as_int(hat_drop_raw.get("chance_pct") or 0))),
            "extra_data": {str(k): v for k, v in extra_data.items()},
        },
    }


def _normalize_ambush(raw):
    if not isinstance(raw, dict) or not raw.get("enabled"):
        return {"enabled": False}

    variants = {}
    for variant_id, variant_raw in (raw.get("variants") or {}).items():
        variant = _normalize_variant(variant_id, variant_raw)
        if variant:
            variants[variant["key"]] = variant

    waves = []
    for wave_raw in raw.get("waves") or []:
        wave = _normalize_wave(wave_raw)
        if wave:
            waves.append(wave)

    return {
        "enabled": True,
        "chance_pct": max(0, min(100, _as_int(raw.get("chance_pct") or 0))),
        "prelude_seconds": max(1, _as_int(raw.get("prelude_seconds") or 8)),
        "dead_party_fail_seconds": max(5, _as_int(raw.get("dead_party_fail_seconds") or 60)),
        "loot_window_seconds": max(5, _as_int(raw.get("loot_window_seconds") or 30)),
        "inter_wave_delay_seconds": max(0, _as_int(raw.get("inter_wave_delay_seconds") or 0)),
        "trigger_progress_min_pct": max(1, min(95, _as_int(raw.get("trigger_progress_min_pct") or 50))),
        "trigger_progress_max_pct": max(1, min(95, _as_int(raw.get("trigger_progress_max_pct") or 65))),
        "average_level_floor": max(1, _as_int(raw.get("average_level_floor") or 1)),
        "average_level_ceiling": max(1, _as_int(raw.get("average_level_ceiling") or 100)),
        "average_level_scale_pct": max(25, min(150, _as_int(raw.get("average_level_scale_pct") or 100))),
        "average_level_bias": _as_int(raw.get("average_level_bias") or 0),
        "captain_extra_boxes_min": max(0, _as_int(raw.get("captain_extra_boxes_min") or 0)),
        "captain_extra_boxes_max": max(0, _as_int(raw.get("captain_extra_boxes_max") or 0)),
        "hat_drop_chance_pct": max(0, min(100, _as_int(raw.get("hat_drop_chance_pct") or 0))),
        "prelude_messages": [_as_str(line) for line in (raw.get("prelude_messages") or []) if _as_str(line)],
        "approach_messages": [_as_str(line) for line in (raw.get("approach_messages") or []) if _as_str(line)],
        "wave_completion_messages": [_as_str(line) for line in (raw.get("wave_completion_messages") or []) if _as_str(line)],
        "boss_arrival_messages": [_as_str(line) for line in (raw.get("boss_arrival_messages") or []) if _as_str(line)],
        "failure_messages": [_as_str(line) for line in (raw.get("failure_messages") or []) if _as_str(line)],
        "success_messages": [_as_str(line) for line in (raw.get("success_messages") or []) if _as_str(line)],
        "variants": variants,
        "waves": waves,
    }


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
                side = _normalize_side(side_raw)
                if side:
                    sides[_as_str(side_name).lower()] = side
            if len(sides) < 2:
                continue

            ferry_room_id = _as_int(raw.get("ferry_room_id") or 0)
            if ferry_room_id <= 0:
                continue

            onboard_room_ids = _as_int_list(raw.get("onboard_room_ids") or [])
            if ferry_room_id not in onboard_room_ids:
                onboard_room_ids.insert(0, ferry_room_id)

            underway_room_ids = _as_int_list(raw.get("underway_room_ids") or [])

            room_transitions_raw = raw.get("room_transitions") or {}
            if not isinstance(room_transitions_raw, dict):
                room_transitions_raw = {}
            room_transitions = {"underway": {}, "docked": {}}
            for mode in ("underway", "docked"):
                room_transitions[mode] = _normalize_room_transition_mapping(room_transitions_raw.get(mode) or {})

            fallback_transitions = _fallback_room_transitions(onboard_room_ids, underway_room_ids)
            for mode in ("underway", "docked"):
                if not room_transitions[mode]:
                    room_transitions[mode] = dict(fallback_transitions.get(mode) or {})

            audio_raw = raw.get("audio") or {}
            if not isinstance(audio_raw, dict):
                audio_raw = {}

            result[_as_str(ferry_id)] = {
                "id": _as_str(raw.get("id") or ferry_id),
                "name": _as_str(raw.get("name") or ferry_id),
                "ferry_room_id": ferry_room_id,
                "onboard_room_ids": onboard_room_ids,
                "underway_room_ids": underway_room_ids,
                "room_transitions": room_transitions,
                "boarding_exit": _as_str(raw.get("boarding_exit") or "go_plank"),
                "dock_duration_sec": max(5, _as_int(raw.get("dock_duration_sec") or 60)),
                "travel_duration_sec": max(5, _as_int(raw.get("travel_duration_sec") or 60)),
                "start_side": _as_str(raw.get("start_side") or next(iter(sides.keys()))).lower(),
                "lore_broadcast_interval_sec": max(5, _as_int(raw.get("lore_broadcast_interval_sec") or 20)),
                "ferry_look": _as_str(raw.get("ferry_look")),
                "ferryman_look": _as_str(raw.get("ferryman_look")),
                "onboard_depart_msg": _as_str(raw.get("onboard_depart_msg")),
                "onboard_arrive_msg": _as_str(raw.get("onboard_arrive_msg")),
                "waiting_room_lines": [_as_str(line) for line in (raw.get("waiting_room_lines") or []) if _as_str(line)],
                "waiting_room_countdown_lines": _normalize_countdown_lines(raw.get("waiting_room_countdown_lines") or []),
                "onboard_status_lines": {
                    _as_str(key): [_as_str(line) for line in (value or []) if _as_str(line)]
                    for key, value in (raw.get("onboard_status_lines") or {}).items()
                    if isinstance(value, list)
                },
                "travel_messages": [_as_str(line) for line in (raw.get("travel_messages") or []) if _as_str(line)],
                "loot_window_messages": [_as_str(line) for line in (raw.get("loot_window_messages") or []) if _as_str(line)],
                "audio": {
                    "default_zone": _as_str(audio_raw.get("default_zone")),
                    "event_zone": _as_str(audio_raw.get("event_zone")),
                },
                "ambush": _normalize_ambush(raw.get("ambush") or {}),
                "sides": sides,
            }

        log.info("ferries_loader: loaded %d ferry routes from Lua", len(result))
        return result

    except Exception as e:
        log.error("ferries_loader: failed to load ferries (%s)", e, exc_info=True)
        return {}
