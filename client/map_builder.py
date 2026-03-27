#!/usr/bin/env python3
"""
map_builder.py — GemStone IV Private Server
Builds data/room_graph.json for the client HUD's pathfinder and exit links.

Sources (applied in order, Lua wins on conflict):
  1. Database  — rooms, room_exits, zones tables  (33k+ rooms)
  2. Lua files — scripts/zones/*/rooms/*.lua       (hand-crafted rooms, override DB)

Every exit (cardinal, go_, climb_, special, hidden) is included so the client
renders clickable links for all of them.

Usage:
    python client/map_builder.py
    python client/map_builder.py --config C:/GemStoneIVServer/config/database/database.yml
    python client/map_builder.py --lua-only
"""

import os
import re
import sys
import json
import argparse


# ── Lua file parsers ──────────────────────────────────────────────────────────

def parse_room_lua(filepath):
    data  = {}
    exits = {}
    in_exits = False

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("--"):
            continue

        if re.match(r"Room\.exits\s*=\s*\{", line):
            in_exits = True
            continue

        if in_exits:
            if "}" in line:
                in_exits = False
                continue
            m = re.match(r"(\w+)\s*=\s*(\d+)", line)
            if m:
                exits[m.group(1)] = int(m.group(2))
            continue

        m = re.match(r"Room\.(\w+)\s*=\s*(.*)", line)
        if not m:
            continue
        key     = m.group(1)
        raw_val = m.group(2).strip().rstrip(",")

        if key == "id":
            try:    data["id"] = int(raw_val)
            except: pass
        elif key == "title":
            data["title"] = raw_val.strip('"\'')
        elif key == "zone_id":
            try:    data["zone_id"] = int(raw_val)
            except: pass
        elif key in ("safe", "supernode", "indoor", "dark", "climbable"):
            data[key] = raw_val.lower() == "true"

    if "id" not in data or data["id"] == 0:
        return None

    data["exits"] = exits
    data.setdefault("title", f"Room {data['id']}")
    data.setdefault("zone_id", 0)
    return data


def parse_zone_lua(filepath):
    zone = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                m = re.match(r"Zone\.(\w+)\s*=\s*(.*)", line)
                if not m:
                    continue
                key, raw = m.group(1), m.group(2).strip().rstrip(",")
                if key == "id":
                    try:    zone["id"] = int(raw)
                    except: pass
                elif key == "name":
                    zone["name"] = raw.strip('"\'')
    except OSError:
        pass
    return zone


# ── Database loader ───────────────────────────────────────────────────────────

def load_db_config(config_path):
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        dev = cfg["database"]["development"]
        return {
            "host":     dev.get("host",     "127.0.0.1"),
            "port":     int(dev.get("port", 3306)),
            "database": dev.get("database", "gemstone_dev"),
            "user":     dev.get("username", "root"),
            "password": dev.get("password", ""),
        }
    except Exception as e:
        print(f"[map_builder] Could not read DB config: {e}")
        return {}


def build_from_db(db_cfg):
    try:
        import mysql.connector
    except ImportError:
        print("[map_builder] mysql-connector-python not installed — skipping DB.")
        print("             Run: pip install mysql-connector-python")
        return {}, {}

    rooms = {}
    zones = {}

    try:
        conn = mysql.connector.connect(**db_cfg, autocommit=True)
        cur  = conn.cursor(dictionary=True)

        # zones
        cur.execute(
            "SELECT id, slug, name FROM zones WHERE is_enabled = 1"
        )
        for row in cur.fetchall():
            zid = str(row["id"])
            zones[zid] = {
                "id":     row["id"],
                "name":   row.get("name") or row.get("slug", ""),
                "folder": row.get("slug", ""),
            }
        print(f"[map_builder] DB zones: {len(zones)}")

        # rooms
        cur.execute("""
            SELECT
                id, zone_id, title, location_name,
                is_safe AS safe, is_supernode AS supernode,
                COALESCE(indoor, is_indoor, 0) AS indoor
            FROM rooms
        """)
        for row in cur.fetchall():
            rid      = str(row["id"])
            zone_id  = row["zone_id"]
            zone_rec = zones.get(str(zone_id), {})
            zone_nm  = zone_rec.get("name", f"Zone {zone_id}")

            location = row.get("location_name") or row.get("title") or ""
            if location and not location.startswith(zone_nm):
                full_title = f"{zone_nm}, {location}"
            else:
                full_title = location or zone_nm

            rooms[rid] = {
                "id":          row["id"],
                "zone_id":     zone_id,
                "title":       full_title,
                "indoor":      bool(row.get("indoor", False)),
                "safe":        bool(row.get("safe",   False)),
                "supernode":   bool(row.get("supernode", False)),
                "exits":       {},
                "zone_name":   zone_nm,
                "zone_folder": zone_rec.get("folder", ""),
            }
        print(f"[map_builder] DB rooms: {len(rooms)}")

        # exits — ALL of them, no filtering on hidden/special
        cur.execute(
            "SELECT room_id, direction, target_room_id FROM room_exits"
        )
        exit_count = 0
        for row in cur.fetchall():
            rid = str(row["room_id"])
            if rid not in rooms:
                continue
            rooms[rid]["exits"][row["direction"]] = row["target_room_id"]
            exit_count += 1
        print(f"[map_builder] DB exits: {exit_count}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"[map_builder] DB error: {e}")
        import traceback; traceback.print_exc()

    return rooms, zones


# ── Lua loader ────────────────────────────────────────────────────────────────

def build_from_lua(scripts_dir):
    scripts_dir = os.path.abspath(scripts_dir)
    zones_dir   = os.path.join(scripts_dir, "zones")
    rooms = {}
    zones = {}

    if not os.path.isdir(zones_dir):
        print(f"[map_builder] Zones dir not found: {zones_dir} — skipping Lua")
        return rooms, zones

    print(f"[map_builder] Scanning Lua: {zones_dir}")
    room_count = skip_count = 0

    for zone_folder in sorted(os.listdir(zones_dir)):
        zone_path = os.path.join(zones_dir, zone_folder)
        if not os.path.isdir(zone_path) or zone_folder.startswith("_"):
            continue

        zone_lua  = os.path.join(zone_path, "zone.lua")
        zone_meta = parse_zone_lua(zone_lua) if os.path.exists(zone_lua) else {}
        zone_meta.setdefault("name",   zone_folder.replace("_", " ").title())
        zone_meta.setdefault("folder", zone_folder)
        zone_id = zone_meta.get("id", 0)
        if zone_id:
            zones[str(zone_id)] = zone_meta

        rooms_dir = os.path.join(zone_path, "rooms")
        if not os.path.isdir(rooms_dir):
            continue

        for fname in sorted(os.listdir(rooms_dir)):
            if not fname.endswith(".lua"):
                continue
            room = parse_room_lua(os.path.join(rooms_dir, fname))
            if room is None:
                skip_count += 1
                continue

            rid = str(room["id"])
            room["zone_name"]   = zone_meta["name"]
            room["zone_folder"] = zone_folder
            # Ensure GS4-style title format
            if ", " not in room.get("title", ""):
                room["title"] = f"{zone_meta['name']}, {room['title']}"
            rooms[rid] = room
            room_count += 1

    print(f"[map_builder] Lua rooms: {room_count} ({skip_count} skipped)")
    return rooms, zones


# ── Main ──────────────────────────────────────────────────────────────────────

def build_graph(scripts_dir, output_path, db_cfg=None, lua_only=False):
    all_rooms = {}
    all_zones = {}

    # Phase 1 — DB (bulk of the world)
    if not lua_only and db_cfg:
        db_rooms, db_zones = build_from_db(db_cfg)
        all_rooms.update(db_rooms)
        all_zones.update(db_zones)
        print(f"[map_builder] After DB phase: {len(all_rooms):,} rooms")
    elif not lua_only:
        print("[map_builder] No DB config — skipping database phase")

    # Phase 2 — Lua (hand-crafted rooms override DB)
    # BUT: preserve any DB exits that the Lua file doesn't define,
    # so exits like go_ladder that only exist in the DB aren't lost.
    lua_rooms, lua_zones = build_from_lua(scripts_dir)
    overrides = 0
    for rid, lua_room in lua_rooms.items():
        if rid in all_rooms:
            overrides += 1
            db_exits = all_rooms[rid].get("exits", {})
            lua_exits = lua_room.get("exits", {})
            # Merge: Lua exits win on conflict, DB-only exits are kept
            merged_exits = {**db_exits, **lua_exits}
            lua_room["exits"] = merged_exits
        all_rooms[rid] = lua_room

    # Update zones — Lua zone names are canonical (e.g. "Ta'Vaalor" beats "the Blighted Forest")
    # Also retroactively fix zone_name on DB rooms that share the same zone_id
    zone_id_to_lua_name = {}
    for zid_str, zmeta in lua_zones.items():
        zone_id_to_lua_name[int(zid_str)] = zmeta["name"]

    all_zones.update(lua_zones)

    fixed_zone_names = 0
    for rid, room in all_rooms.items():
        zid = room.get("zone_id")
        if zid and zid in zone_id_to_lua_name:
            canonical = zone_id_to_lua_name[zid]
            if room.get("zone_name") != canonical:
                room["zone_name"] = canonical
                # Also fix the title prefix if it used the old zone name
                title = room.get("title", "")
                old_prefix = next(
                    (n for n in [room.get("zone_name", ""), ""]
                     if title.startswith(n + ", ")), None
                )
                if old_prefix and old_prefix != canonical:
                    room["title"] = canonical + title[len(old_prefix):]
                fixed_zone_names += 1

    print(f"[map_builder] After Lua phase: {len(all_rooms):,} rooms "
          f"({overrides} DB rooms merged with Lua, {fixed_zone_names} zone names normalised)")

    # Dangling exit report
    all_ids  = set(int(k) for k in all_rooms)
    dangling = sum(
        1 for r in all_rooms.values()
        for tid in r.get("exits", {}).values()
        if tid not in all_ids
    )
    if dangling:
        print(f"[map_builder] Note: {dangling:,} exits reference unknown rooms "
              f"(cross-server premium areas — normal)")

    graph = {
        "version":    2,
        "room_count": len(all_rooms),
        "zones":      all_zones,
        "rooms":      all_rooms,
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, separators=(",", ":"), ensure_ascii=False)

    print(f"[map_builder] Written: {output_path}")
    return graph


def main():
    here            = os.path.dirname(os.path.abspath(__file__))
    default_scripts = os.path.normpath(os.path.join(here, "..", "scripts"))
    default_out     = os.path.join(here, "data", "room_graph.json")
    default_cfg     = os.path.normpath(
        os.path.join(here, "..", "config", "database", "database.yml")
    )

    parser = argparse.ArgumentParser(
        description="Build room_graph.json for the GemStone IV HUD."
    )
    parser.add_argument("--scripts",  default=default_scripts)
    parser.add_argument("--out",      default=default_out)
    parser.add_argument("--config",   default=default_cfg)
    parser.add_argument("--lua-only", action="store_true",
                        help="Skip the database; load Lua files only")
    args = parser.parse_args()

    print("=" * 60)
    print("  GemStone IV — Room Graph Builder  (DB + Lua)")
    print("=" * 60)

    db_cfg = None
    if not args.lua_only:
        if os.path.exists(args.config):
            db_cfg = load_db_config(args.config)
            if db_cfg:
                print(f"[map_builder] DB: "
                      f"{db_cfg['host']}:{db_cfg['port']}/{db_cfg['database']}")
        else:
            print(f"[map_builder] DB config not found at {args.config} — DB skipped")

    graph = build_graph(args.scripts, args.out, db_cfg=db_cfg, lua_only=args.lua_only)
    print(f"\nDone.  {graph['room_count']:,} rooms ready for the HUD.")
    print("Restart gsiv_hud.py to pick up the new graph.")


if __name__ == "__main__":
    main()
