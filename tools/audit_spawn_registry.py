#!/usr/bin/env python
"""
Audit low/mid-level creature spawns against Lua spawn registries.

This uses:
- scripts/zones/*/spawns.lua as the map-backed population registry
- Lua mob templates + creature catalog entries
- DB room/zone metadata

It reports templates that would be blocked by the runtime spawn-registry guard,
which is useful for spotting zone leakage and catalog clones that are not
explicitly placed on the local maps.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from server.core.entity.creature.lua_mob_loader import load_all_mob_luas
from server.core.entity.creature.lua_spawn_registry_loader import load_zone_spawn_registries


def _mysql_query(database: str, user: str, password: str, sql: str) -> list[list[str]]:
    cmd = ["mysql", "-N", "-B", "-u", user]
    if password:
        cmd.append(f"-p{password}")
    cmd.extend([database, "-e", sql])
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "mysql query failed")
    rows = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        rows.append(line.rstrip("\n").split("\t"))
    return rows


def _chunked(values: list[int], size: int) -> list[list[int]]:
    return [values[i:i + size] for i in range(0, len(values), size)]


def _load_zone_slugs(database: str, user: str, password: str) -> dict[int, str]:
    rows = _mysql_query(database, user, password, "SELECT id, slug FROM zones WHERE is_enabled = 1")
    mapping = {}
    for row in rows:
        if len(row) < 2:
            continue
        try:
            mapping[int(row[0])] = row[1]
        except Exception:
            continue
    return mapping


def _load_room_zone_slugs(database: str, user: str, password: str, room_ids: list[int], zone_slugs: dict[int, str]) -> dict[int, str]:
    room_zone_slugs = {}
    for batch in _chunked(sorted(set(room_ids)), 500):
        sql = f"SELECT id, zone_id FROM rooms WHERE id IN ({','.join(str(v) for v in batch)})"
        for row in _mysql_query(database, user, password, sql):
            if len(row) < 2:
                continue
            try:
                room_id = int(row[0])
                zone_id = int(row[1])
            except Exception:
                continue
            zone_slug = zone_slugs.get(zone_id)
            if zone_slug:
                room_zone_slugs[room_id] = zone_slug
    return room_zone_slugs


def _load_lua_room_zone_slugs(scripts_path: str) -> dict[int, str]:
    room_zone_slugs = {}
    zones_path = os.path.join(scripts_path, "zones")
    if not os.path.isdir(zones_path):
        return room_zone_slugs
    for zone_slug in sorted(os.listdir(zones_path)):
        rooms_path = os.path.join(zones_path, zone_slug, "rooms")
        if not os.path.isdir(rooms_path):
            continue
        for filename in os.listdir(rooms_path):
            if not filename.endswith(".lua"):
                continue
            path = os.path.join(rooms_path, filename)
            try:
                text = open(path, "r", encoding="utf-8").read()
            except OSError:
                continue
            match = re.search(r"Room\.id\s*=\s*(\d+)", text)
            if not match:
                continue
            room_zone_slugs[int(match.group(1))] = zone_slug
    return room_zone_slugs


def _allow_template_in_room(template_id: str, template: dict, room_id: int, room_zone_slug: str, registries: dict) -> bool:
    try:
        level = int((template or {}).get("level", 1) or 1)
    except Exception:
        level = 1
    if level > 35:
        return True

    registry = (registries or {}).get(room_zone_slug)
    if not registry:
        return True

    population = registry.get("population") or {}
    map_locked = bool(registry.get("map_locked", False))
    population_entry = population.get(template_id)
    mob_rooms = registry.get("mob_rooms") or {}
    depth_rooms = registry.get("depth_rooms") or {}

    if template_id in mob_rooms:
        return int(room_id) in {int(v) for v in (mob_rooms.get(template_id) or [])}

    if population_entry:
        depth_key = str(population_entry.get("depth", "") or "").strip()
        if depth_key and depth_key in depth_rooms:
            return int(room_id) in {int(v) for v in (depth_rooms.get(depth_key) or [])}
        return True

    origin = str((template or {}).get("template_origin", "") or "").strip().lower()
    if not map_locked:
        return True
    if origin == "catalog":
        return False

    source_zones = {
        str(zone).strip()
        for zone in ((template or {}).get("source_zones") or [])
        if str(zone).strip()
    }
    source_zone = str((template or {}).get("source_zone", "") or "").strip()
    if source_zone:
        source_zones.add(source_zone)

    if origin == "authored" and room_zone_slug in source_zones:
        return True

    if origin == "authored":
        return False

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit <=35 spawns against Lua map-backed spawn registries.")
    parser.add_argument("--scripts", default=os.path.join(os.getcwd(), "scripts"))
    parser.add_argument("--database", default=os.environ.get("GS_DB_NAME", "gemstone_dev"))
    parser.add_argument("--db-user", default=os.environ.get("GS_DB_USER", "root"))
    parser.add_argument("--db-password", default=os.environ.get("GS_DB_PASSWORD", ""))
    args = parser.parse_args()

    registries = load_zone_spawn_registries(args.scripts)
    templates = load_all_mob_luas(args.scripts)

    tracked_room_ids = []
    for template in templates.values():
        try:
            level = int(template.get("level", 1) or 1)
        except Exception:
            level = 1
        if level > 35:
            continue
        tracked_room_ids.extend(int(room_id) for room_id in (template.get("spawn_rooms") or []) if isinstance(room_id, int))

    zone_slugs = _load_zone_slugs(args.database, args.db_user, args.db_password)
    room_zone_slugs = _load_lua_room_zone_slugs(args.scripts)
    missing_room_ids = [room_id for room_id in tracked_room_ids if room_id not in room_zone_slugs]
    room_zone_slugs.update(
        _load_room_zone_slugs(args.database, args.db_user, args.db_password, missing_room_ids, zone_slugs)
    )

    blocked = {}
    for template_id, template in sorted(templates.items()):
        try:
            level = int(template.get("level", 1) or 1)
        except Exception:
            level = 1
        if level > 35:
            continue
        for room_id in template.get("spawn_rooms") or []:
            if not isinstance(room_id, int):
                continue
            room_zone_slug = room_zone_slugs.get(room_id)
            if not room_zone_slug:
                continue
            if _allow_template_in_room(template_id, template, room_id, room_zone_slug, registries):
                continue
            entry = blocked.setdefault(template_id, {
                "origin": str(template.get("template_origin") or "unknown"),
                "level": level,
                "zones": set(),
                "rooms": set(),
            })
            entry["zones"].add(room_zone_slug)
            entry["rooms"].add(room_id)

    if not blocked:
        print("No blocked <=35 spawn templates found.")
        return 0

    print(f"Blocked <=35 spawn templates: {len(blocked)}")
    for template_id, info in sorted(blocked.items(), key=lambda row: (-len(row[1]['rooms']), row[0])):
        zones = ", ".join(sorted(info["zones"])) or "unknown"
        print(
            f"{template_id}\torigin={info['origin']}\tlevel={info['level']}\t"
            f"rooms={len(info['rooms'])}\tzones={zones}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
