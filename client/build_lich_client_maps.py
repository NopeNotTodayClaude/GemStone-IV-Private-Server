#!/usr/bin/env python3
"""
Build client room graph + map regions from Lich's GSIV map JSON.

This keeps server-only/custom rooms from the existing client data, but replaces
Lich-backed rooms/maps with authoritative Lich image, coordinate, and wayto data.
"""

import argparse
import json
import os
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path


ROOT_DIR = str(Path(os.environ.get("GEMSTONE_ROOT") or Path(__file__).resolve().parents[1]).resolve())
CLIENT_DIR = os.path.join(ROOT_DIR, "client")
DATA_DIR = os.path.join(CLIENT_DIR, "data")
GRAPH_PATH = os.path.join(DATA_DIR, "room_graph.json")
REGIONS_PATH = os.path.join(DATA_DIR, "map_regions.json")
_LICH_ROOT = os.environ.get("LICH_ROOT") or os.environ.get("RUBY4LICH_ROOT") or ""

DEFAULT_LICH_JSON_CANDIDATES = [
    str(Path(_LICH_ROOT).expanduser() / "data" / "GSIV" / "map-1773601222.json") if _LICH_ROOT else "",
    os.path.join(ROOT_DIR, "map-1773601222.json"),
]
DEFAULT_ROOM_EXITS_TSV = os.path.join(ROOT_DIR, "tmp_room_exits.tsv")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path: str, data: dict):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")


def find_existing_path(candidates: List[str]) -> Optional[str]:
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


def slugify_command(command: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", command.strip().lower())
    key = re.sub(r"_+", "_", key).strip("_")
    return key or "command"


def extract_command(raw: object) -> Optional[str]:
    command = str(raw or "").strip()
    if not command:
        return None

    if not command.startswith(";"):
        return command

    nuisance = {"hide", "unhide", "stand", "sit", "kneel"}
    candidates = []
    for pattern in (
        r'move\s*\(\s*"([^"#{}][^"]*)"',
        r"move\s*\(\s*'([^'#{}][^']*)'",
        r'fput\s+"([^"#{}][^"]*)"',
        r"fput\s+'([^'#{}][^']*)'",
        r'dothistimeout\s*\(\s*"([^"#{}][^"]*)"',
        r"dothistimeout\s*\(\s*'([^'#{}][^']*)'",
    ):
        for match in re.finditer(pattern, command, re.IGNORECASE):
            extracted = match.group(1).strip()
            if extracted:
                candidates.append(extracted)

    for extracted in reversed(candidates):
        if extracted.lower() not in nuisance:
            return extracted
    if candidates:
        return candidates[-1]

    return None


def image_coords_to_box(coords: object) -> Optional[Tuple[int, int, int, int]]:
    if not isinstance(coords, list) or len(coords) != 4:
        return None
    try:
        x1, y1, x2, y2 = [int(v) for v in coords]
    except (TypeError, ValueError):
        return None
    left = min(x1, x2)
    top = min(y1, y2)
    width = max(8, abs(x2 - x1))
    height = max(8, abs(y2 - y1))
    return left, top, width, height


def parse_visible_paths(raw_paths: object) -> List[str]:
    values = raw_paths if isinstance(raw_paths, list) else [raw_paths]
    tokens: List[str] = []
    for value in values:
        text = str(value or "").strip()
        if ":" in text:
            text = text.split(":", 1)[1].strip()
        for part in text.split(","):
            key = slugify_command(part)
            if key:
                tokens.append(key)
    return tokens


def load_existing_graph(path: str) -> Dict[int, dict]:
    if not os.path.exists(path):
        return {}
    data = load_json(path)
    result: Dict[int, dict] = {}
    for rid_str, room in (data.get("rooms") or {}).items():
        try:
            rid = int(rid_str)
        except (TypeError, ValueError):
            continue
        result[rid] = room
    return result


def load_existing_regions(path: str) -> Dict[str, dict]:
    if not os.path.exists(path):
        return {}
    data = load_json(path)
    return data.get("maps") or {}


def load_local_room_exit_overrides(root_dir: str) -> Dict[int, Dict[str, int]]:
    overrides: Dict[int, Dict[str, int]] = {}
    rooms_root = os.path.join(root_dir, "scripts", "zones")
    if not os.path.isdir(rooms_root):
        return overrides

    room_id_re = re.compile(r"Room\.id\s*=\s*(\d+)")
    exits_block_re = re.compile(r"Room\.exits\s*=\s*\{(.*?)\}", re.DOTALL)
    exit_line_re = re.compile(r"([a-zA-Z0-9_]+)\s*=\s*(\d+)")

    for zone_name in os.listdir(rooms_root):
        zone_dir = os.path.join(rooms_root, zone_name)
        rooms_dir = os.path.join(zone_dir, "rooms")
        if not os.path.isdir(rooms_dir):
            continue
        for file_name in os.listdir(rooms_dir):
            if not file_name.lower().endswith(".lua"):
                continue
            path = os.path.join(rooms_dir, file_name)
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    text = f.read()
            except Exception:
                continue
            room_id_match = room_id_re.search(text)
            exits_match = exits_block_re.search(text)
            if not room_id_match or not exits_match:
                continue
            try:
                room_id = int(room_id_match.group(1))
            except ValueError:
                continue
            exits: Dict[str, int] = {}
            for key, target in exit_line_re.findall(exits_match.group(1)):
                try:
                    exits[str(key).strip()] = int(target)
                except ValueError:
                    continue
            if exits:
                overrides[room_id] = exits
    return overrides


def load_room_exits_tsv(path: str) -> Dict[int, List[dict]]:
    result: Dict[int, List[dict]] = defaultdict(list)
    if not path or not os.path.exists(path):
        return result
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            try:
                room_id = int(parts[0])
                target_room_id = int(parts[3])
                is_hidden = int(parts[4] or "0")
                is_special = int(parts[5] or "0")
                search_dc = int(parts[6] or "0")
            except (TypeError, ValueError):
                continue
            result[room_id].append({
                "direction": str(parts[1] or "").strip(),
                "exit_verb": str(parts[2] or "").strip(),
                "target_room_id": target_room_id,
                "is_hidden": bool(is_hidden),
                "is_special": bool(is_special),
                "search_dc": search_dc,
            })
    return result


def build_from_lich_json(path: str) -> Tuple[Dict[int, dict], Dict[str, dict]]:
    data = load_json(path)
    if not isinstance(data, list):
        raise ValueError("Expected Lich map JSON to be a list of room entries")

    rooms: Dict[int, dict] = {}
    regions: Dict[str, dict] = {}

    for entry in data:
        if not isinstance(entry, dict):
            continue

        try:
            rid = int(entry["id"])
        except (KeyError, TypeError, ValueError):
            continue

        image_name = str(entry.get("image") or "").strip()
        region_name = os.path.splitext(os.path.basename(image_name))[0] if image_name else ""

        room = {
            "id": rid,
            "title": (entry.get("title") or [""])[0] if isinstance(entry.get("title"), list) else str(entry.get("title") or ""),
            "zone_name": str(entry.get("location") or region_name or ""),
            "region_name": region_name,
            "location": str(entry.get("location") or ""),
            "image": image_name,
            "image_coords": entry.get("image_coords"),
            "uid": list(entry.get("uid") or []),
            "lich_uid": (entry.get("uid") or [None])[-1],
            "climate": entry.get("climate"),
            "terrain": entry.get("terrain"),
            "tags": [str(tag).strip().lower() for tag in (entry.get("tags") or []) if str(tag).strip()],
            "visible_paths": parse_visible_paths(entry.get("paths")),
            "exits": {},
            "edges": [],
        }

        wayto = entry.get("wayto") or {}
        timeto = entry.get("timeto") or {}
        if isinstance(wayto, dict):
            for target_str, raw_command in wayto.items():
                try:
                    target_id = int(target_str)
                except (TypeError, ValueError):
                    continue
                command = extract_command(raw_command)
                if not command:
                    continue
                key = slugify_command(command)
                try:
                    cost = float(timeto.get(str(target_id), timeto.get(target_id, 1.0)))
                except (TypeError, ValueError):
                    cost = 1.0
                room["edges"].append({
                    "to": target_id,
                    "command": command,
                    "key": key,
                    "cost": max(0.05, cost),
                })
                room["exits"].setdefault(key, target_id)

        rooms[rid] = room

        box = image_coords_to_box(entry.get("image_coords"))
        if image_name and box:
            region = regions.setdefault(region_name, {"image": image_name, "rooms": {}})
            region["rooms"][str(rid)] = list(box)

    return rooms, regions


def apply_local_exit_overrides(rooms: Dict[int, dict], overrides: Dict[int, Dict[str, int]]) -> None:
    for rid, local_exits in overrides.items():
        room = rooms.get(rid)
        if not room or not local_exits:
            continue

        existing_edges = list(room.get("edges") or [])
        edge_by_target = {int(edge.get("to")): edge for edge in existing_edges if edge.get("to") is not None}
        rebuilt_edges = []
        used_targets = set()

        for key, target_id in local_exits.items():
            command = key.replace("_", " ")
            edge = edge_by_target.get(target_id)
            if edge:
                edge = dict(edge)
                edge["key"] = key
                edge["command"] = command
                rebuilt_edges.append(edge)
            else:
                rebuilt_edges.append({
                    "to": target_id,
                    "command": command,
                    "key": key,
                    "cost": 0.2,
                })
            used_targets.add(target_id)

        for edge in existing_edges:
            try:
                target_id = int(edge.get("to"))
            except (TypeError, ValueError):
                continue
            if target_id in used_targets:
                continue
            rebuilt_edges.append(edge)

        room["edges"] = rebuilt_edges
        rebuilt_exits: Dict[str, int] = {}
        for edge in rebuilt_edges:
            key = str(edge.get("key") or "").strip()
            try:
                target_id = int(edge.get("to"))
            except (TypeError, ValueError):
                continue
            if key:
                rebuilt_exits.setdefault(key, target_id)
        room["exits"] = rebuilt_exits


def apply_room_exit_fallbacks(rooms: Dict[int, dict], db_room_exits: Dict[int, List[dict]]) -> None:
    for rid, rows in db_room_exits.items():
        room = rooms.get(rid)
        if not room or not rows:
            continue

        existing_edges = list(room.get("edges") or [])
        existing_keys = {str(edge.get("key") or "").strip() for edge in existing_edges}
        existing_targets = {int(edge.get("to")) for edge in existing_edges if edge.get("to") is not None}

        add_rows = []
        for row in rows:
            if row.get("is_hidden"):
                continue
            direction = slugify_command(row.get("direction") or "")
            target_id = int(row.get("target_room_id"))
            if not direction:
                continue
            # Prefer Lich simple wayto data whenever it exists, but backfill
            # rooms/targets that the Lich script left disconnected.
            if direction in existing_keys or target_id in existing_targets:
                continue
            add_rows.append({
                "to": target_id,
                "command": str(row.get("direction") or "").replace("_", " "),
                "key": direction,
                "cost": 0.2,
            })

        if not add_rows:
            continue

        room["edges"] = existing_edges + add_rows
        rebuilt_exits = dict(room.get("exits") or {})
        for edge in add_rows:
            rebuilt_exits.setdefault(edge["key"], edge["to"])
        room["exits"] = rebuilt_exits


def apply_reciprocal_compass_inference(rooms: Dict[int, dict]) -> None:
    opposites = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east",
        "northeast": "southwest",
        "southwest": "northeast",
        "northwest": "southeast",
        "southeast": "northwest",
        "up": "down",
        "down": "up",
        "in": "out",
        "out": "in",
    }
    incoming: Dict[int, List[Tuple[int, str]]] = defaultdict(list)
    for rid, room in rooms.items():
        for edge in room.get("edges") or []:
            try:
                target_id = int(edge.get("to"))
            except (TypeError, ValueError):
                continue
            key = str(edge.get("key") or "").strip()
            if key in opposites:
                incoming[target_id].append((rid, key))

    for rid, room in rooms.items():
        visible = set(room.get("visible_paths") or [])
        if not visible:
            continue
        exits = dict(room.get("exits") or {})
        edges = list(room.get("edges") or [])
        existing_keys = set(exits.keys())
        for source_id, source_key in incoming.get(rid, []):
            reverse_key = opposites.get(source_key)
            if not reverse_key or reverse_key not in visible or reverse_key in existing_keys:
                continue
            exits[reverse_key] = source_id
            edges.append({
                "to": source_id,
                "command": reverse_key.replace("_", " "),
                "key": reverse_key,
                "cost": 0.2,
            })
            existing_keys.add(reverse_key)
        room["exits"] = exits
        room["edges"] = edges


def merge_rooms(base_rooms: Dict[int, dict], lich_rooms: Dict[int, dict]) -> Dict[str, dict]:
    merged: Dict[str, dict] = {}
    all_ids = sorted(set(base_rooms) | set(lich_rooms))
    for rid in all_ids:
        if rid in lich_rooms:
            merged[str(rid)] = lich_rooms[rid]
        else:
            merged[str(rid)] = base_rooms[rid]
    return merged


def merge_regions(base_regions: Dict[str, dict], lich_regions: Dict[str, dict], lich_room_ids: set) -> Dict[str, dict]:
    merged: Dict[str, dict] = {}

    for region_name, region_data in base_regions.items():
        rooms = {}
        for rid_str, coords in (region_data.get("rooms") or {}).items():
            try:
                rid = int(rid_str)
            except (TypeError, ValueError):
                continue
            if rid in lich_room_ids:
                continue
            rooms[str(rid)] = coords
        merged[region_name] = {
            "image": region_data.get("image", ""),
            "rooms": rooms,
        }

    for region_name, region_data in lich_regions.items():
        merged[region_name] = region_data

    return dict(sorted(merged.items(), key=lambda item: item[0].lower()))


def main():
    parser = argparse.ArgumentParser(description="Build client graph/regions from Lich GSIV map JSON")
    parser.add_argument("--lich-json", default=None, help="Path to Lich GSIV map JSON")
    parser.add_argument("--graph-out", default=GRAPH_PATH, help="Output room_graph.json path")
    parser.add_argument("--regions-out", default=REGIONS_PATH, help="Output map_regions.json path")
    parser.add_argument("--base-graph", default=GRAPH_PATH, help="Existing room_graph.json to preserve custom rooms from")
    parser.add_argument("--base-regions", default=REGIONS_PATH, help="Existing map_regions.json to preserve custom maps from")
    parser.add_argument("--room-exits-tsv", default=DEFAULT_ROOM_EXITS_TSV, help="Optional TSV export of room_exits for fallback graph edges")
    args = parser.parse_args()

    lich_json_path = args.lich_json or find_existing_path(DEFAULT_LICH_JSON_CANDIDATES)
    if not lich_json_path:
        raise SystemExit("Could not find Lich map JSON")

    base_rooms = load_existing_graph(args.base_graph)
    base_regions = load_existing_regions(args.base_regions)
    lich_rooms, lich_regions = build_from_lich_json(lich_json_path)
    local_exit_overrides = load_local_room_exit_overrides(ROOT_DIR)
    db_room_exits = load_room_exits_tsv(args.room_exits_tsv)
    # Only use local file exits to rescue rooms that Lich could not model at all.
    local_exit_overrides = {rid: exits for rid, exits in local_exit_overrides.items() if not lich_rooms.get(rid, {}).get("edges")}
    apply_local_exit_overrides(lich_rooms, local_exit_overrides)
    apply_room_exit_fallbacks(lich_rooms, db_room_exits)
    apply_reciprocal_compass_inference(lich_rooms)

    merged_rooms = merge_rooms(base_rooms, lich_rooms)
    merged_regions = merge_regions(base_regions, lich_regions, set(lich_rooms))

    save_json(args.graph_out, {"rooms": merged_rooms})
    save_json(args.regions_out, {"maps": merged_regions})

    print(f"Lich JSON: {lich_json_path}")
    print(f"Lich-backed rooms: {len(lich_rooms)}")
    print(f"Preserved custom rooms: {len([rid for rid in base_rooms if rid not in lich_rooms])}")
    print(f"Map regions written: {len(merged_regions)}")
    print(f"Graph output: {args.graph_out}")
    print(f"Regions output: {args.regions_out}")


if __name__ == "__main__":
    main()
