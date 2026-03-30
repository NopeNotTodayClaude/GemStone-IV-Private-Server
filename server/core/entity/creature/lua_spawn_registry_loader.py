"""
lua_spawn_registry_loader.py
----------------------------
Loads scripts/zones/<zone>/spawns.lua as the authoritative, Lua-authored
population registry for map-backed hunting zones.

This registry is used to keep low/mid-level hunting grounds aligned with the
map/image-driven population definitions without hardcoding zone spawn rules in
Python.
"""

import os
import logging

from lupa import LuaRuntime  # type: ignore

log = logging.getLogger(__name__)


def _lua_table_to_python(tbl):
    if tbl is None:
        return None
    if hasattr(tbl, "items"):
        items = list(tbl.items())
        if items and all(isinstance(k, int) for k, _ in items):
            return [_lua_table_to_python(v) for _, v in sorted(items, key=lambda row: row[0])]
        return {k: _lua_table_to_python(v) for k, v in items}
    return tbl


def _normalize_population(raw_population) -> dict:
    population = {}
    for entry in raw_population or []:
        if not isinstance(entry, dict):
            continue
        template_id = str(entry.get("mob") or "").strip()
        if not template_id:
            continue
        try:
            level = int(entry.get("level", 0) or 0)
        except Exception:
            level = 0
        try:
            max_count = int(entry.get("max", 0) or 0)
        except Exception:
            max_count = 0
        depth = str(entry.get("depth", "") or "").strip() or None
        population[template_id] = {
            "template_id": template_id,
            "level": level,
            "max_count": max_count,
            "depth": depth,
        }
    return population


def _normalize_room_groups(raw_groups) -> dict:
    groups = {}
    if not isinstance(raw_groups, dict):
        return groups
    for key, values in raw_groups.items():
        group_key = str(key or "").strip()
        if not group_key:
            continue
        rooms = []
        seen = set()
        for value in values or []:
            try:
                room_id = int(value)
            except Exception:
                continue
            if room_id in seen:
                continue
            seen.add(room_id)
            rooms.append(room_id)
        groups[group_key] = rooms
    return groups


def load_zone_spawn_registries(scripts_path: str) -> dict:
    """Load every scripts/zones/<zone>/spawns.lua into a normalized registry dict."""
    registries = {}
    zones_path = os.path.join(scripts_path, "zones")

    if not os.path.isdir(zones_path):
        log.warning("Spawn registry loader: zones directory not found: %s", zones_path)
        return registries

    lua = LuaRuntime(unpack_returned_tuples=True)

    for zone_slug in sorted(os.listdir(zones_path)):
        zone_path = os.path.join(zones_path, zone_slug)
        if not os.path.isdir(zone_path):
            continue
        registry_path = os.path.join(zone_path, "spawns.lua")
        if not os.path.isfile(registry_path):
            continue
        try:
            with open(registry_path, "r", encoding="utf-8") as handle:
                src = handle.read()
            raw = _lua_table_to_python(lua.execute(src)) or {}
        except Exception as exc:
            log.error("Spawn registry loader failed for %s: %s", registry_path, exc, exc_info=True)
            continue

        room_range = raw.get("room_range") or {}
        registries[zone_slug] = {
            "zone": str(raw.get("zone") or zone_slug),
            "area": str(raw.get("area") or zone_slug.replace("_", " ").title()),
            "map_locked": bool(raw.get("map_locked", False)),
            "room_range": {
                "min": int(room_range.get("min", 0) or 0),
                "max": int(room_range.get("max", 0) or 0),
            } if isinstance(room_range, dict) and room_range else None,
            "population": _normalize_population(raw.get("population") or []),
            "depth_rooms": _normalize_room_groups(raw.get("depth_rooms") or {}),
            "mob_rooms": _normalize_room_groups(raw.get("mob_rooms") or {}),
            "source_file": registry_path,
        }

    log.info("Spawn registry loader: %d zone registries loaded", len(registries))
    return registries
