"""
town_trouble_loader.py
----------------------
Loads scripts/data/town_trouble.lua into a normalized Python dict.
"""

import logging

log = logging.getLogger(__name__)


def _to_int(value, default=0):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return int(default)


def _to_float(value, default=0.0):
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return float(default)


def _to_str_list(values):
    if isinstance(values, (list, tuple)):
        return [str(v).strip() for v in values if str(v).strip()]
    if values is None:
        return []
    text = str(values).strip()
    return [text] if text else []


def _to_int_list(values):
    rows = []
    for raw in values or []:
        iv = _to_int(raw, 0)
        if iv > 0:
            rows.append(iv)
    return rows


def load_town_trouble(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        log.warning("town_trouble_loader: Lua engine unavailable")
        return {
            "config": {},
            "cities": {},
            "districts": {},
            "hostile_variants": {},
            "incidents": {},
        }

    try:
        data = lua_engine.load_data("data/town_trouble") or {}
        if not isinstance(data, dict):
            raise RuntimeError("town_trouble.lua did not return a dict")

        config = dict(data.get("config") or {})
        cities = {}
        districts = {}
        hostile_variants = {}
        incidents = {}

        for city_key, raw in (data.get("cities") or {}).items():
            if not isinstance(raw, dict):
                continue
            key = str(raw.get("key") or city_key or "").strip().lower()
            zone_id = _to_int(raw.get("zone_id"), 0)
            if not key or zone_id <= 0:
                continue
            cities[key] = {
                "key": key,
                "zone_id": zone_id,
                "display_name": str(raw.get("display_name") or key.replace("_", " ").title()).strip(),
                "district_ids": [v.lower() for v in _to_str_list(raw.get("district_ids"))],
            }

        for district_key, raw in (data.get("districts") or {}).items():
            if not isinstance(raw, dict):
                continue
            key = str(raw.get("key") or district_key or "").strip().lower()
            if not key:
                continue
            districts[key] = {
                "key": key,
                "city_key": str(raw.get("city_key") or "").strip().lower(),
                "label": str(raw.get("label") or key.replace("_", " ").title()).strip(),
                "anchor_room_id": _to_int(raw.get("anchor_room_id"), 0),
                "room_ids": _to_int_list(raw.get("room_ids")),
                "scene_lines": _to_str_list(raw.get("scene_lines")),
            }

        for variant_key, raw in (data.get("hostile_variants") or {}).items():
            if not isinstance(raw, dict):
                continue
            key = str(raw.get("key") or variant_key or "").strip().lower()
            base_template_id = str(raw.get("base_template_id") or "").strip()
            if not key or not base_template_id:
                continue
            hostile_variants[key] = {
                "key": key,
                "base_template_id": base_template_id,
                "name": str(raw.get("name") or "").strip(),
                "article": str(raw.get("article") or "a").strip(),
                "description": str(raw.get("description") or "").strip(),
                "level_offset": _to_int(raw.get("level_offset"), 0),
                "hp_mult": max(0.1, _to_float(raw.get("hp_mult"), 1.0)),
                "as_mult": max(0.1, _to_float(raw.get("as_mult"), 1.0)),
                "ds_mult": max(0.1, _to_float(raw.get("ds_mult"), 1.0)),
                "td_mult": max(0.1, _to_float(raw.get("td_mult"), 1.0)),
                "treasure": dict(raw.get("treasure") or {}),
            }

        for incident_key, raw in (data.get("incidents") or {}).items():
            if not isinstance(raw, dict):
                continue
            key = str(raw.get("key") or incident_key or "").strip().lower()
            if not key:
                continue
            stages = []
            for idx, stage_raw in enumerate(raw.get("stages") or []):
                if not isinstance(stage_raw, dict):
                    continue
                hostiles = []
                for hostile_raw in stage_raw.get("hostiles") or []:
                    if not isinstance(hostile_raw, dict):
                        continue
                    variant_id = str(hostile_raw.get("variant_id") or "").strip().lower()
                    count = max(1, _to_int(hostile_raw.get("count"), 1))
                    if variant_id:
                        hostiles.append({"variant_id": variant_id, "count": count})
                if not hostiles:
                    continue
                stages.append({
                    "key": str(stage_raw.get("key") or f"stage_{idx + 1}").strip().lower(),
                    "label": str(stage_raw.get("label") or f"Stage {idx + 1}").strip(),
                    "spawn_room_ids": _to_int_list(stage_raw.get("spawn_room_ids")),
                    "hostiles": hostiles,
                    "completion_announcement": str(stage_raw.get("completion_announcement") or "").strip(),
                })
            rewards = dict(raw.get("rewards") or {})
            incidents[key] = {
                "key": key,
                "city_key": str(raw.get("city_key") or "").strip().lower(),
                "audio_zone_override": str(raw.get("audio_zone_override") or "").strip(),
                "weight": max(1, _to_int(raw.get("weight"), 1)),
                "difficulty": max(1, _to_int(raw.get("difficulty"), 1)),
                "min_duration_seconds": max(120, _to_int(raw.get("min_duration_seconds"), 600)),
                "max_duration_seconds": max(120, _to_int(raw.get("max_duration_seconds"), 900)),
                "district_ids": [v.lower() for v in _to_str_list(raw.get("district_ids"))],
                "room_lines": _to_str_list(raw.get("room_lines")),
                "crier_open": _to_str_list(raw.get("crier_open")),
                "crier_progress": _to_str_list(raw.get("crier_progress")),
                "crier_success": _to_str_list(raw.get("crier_success")),
                "crier_fail": _to_str_list(raw.get("crier_fail")),
                "stages": stages,
                "rewards": {
                    "xp": max(0, _to_int(rewards.get("xp"), 0)),
                    "fame": max(0, _to_int(rewards.get("fame"), 0)),
                    "silver": max(0, _to_int(rewards.get("silver"), 0)),
                    "box_min": max(0, _to_int(rewards.get("box_min"), 0)),
                    "box_max": max(0, _to_int(rewards.get("box_max"), 0)),
                    "box_level_bonus": max(0, _to_int(rewards.get("box_level_bonus"), 0)),
                },
            }

        log.info(
            "town_trouble_loader: loaded %d cities, %d districts, %d variants, %d incidents",
            len(cities),
            len(districts),
            len(hostile_variants),
            len(incidents),
        )
        return {
            "config": config,
            "cities": cities,
            "districts": districts,
            "hostile_variants": hostile_variants,
            "incidents": incidents,
        }
    except Exception as e:
        log.error("town_trouble_loader: failed to load town_trouble.lua (%s)", e, exc_info=True)
        return {
            "config": {},
            "cities": {},
            "districts": {},
            "hostile_variants": {},
            "incidents": {},
        }
