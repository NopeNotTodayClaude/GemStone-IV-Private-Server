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


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_DIR = os.path.join(ROOT_DIR, "client")
DATA_DIR = os.path.join(CLIENT_DIR, "data")
GRAPH_PATH = os.path.join(DATA_DIR, "room_graph.json")
REGIONS_PATH = os.path.join(DATA_DIR, "map_regions.json")

DEFAULT_LICH_JSON_CANDIDATES = [
    r"N:\Ruby4Lich5\R4LInstall\Lich5.15.1\data\GSIV\map-1773601222.json",
    os.path.join(ROOT_DIR, "map-1773601222.json"),
]


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
    args = parser.parse_args()

    lich_json_path = args.lich_json or find_existing_path(DEFAULT_LICH_JSON_CANDIDATES)
    if not lich_json_path:
        raise SystemExit("Could not find Lich map JSON")

    base_rooms = load_existing_graph(args.base_graph)
    base_regions = load_existing_regions(args.base_regions)
    lich_rooms, lich_regions = build_from_lich_json(lich_json_path)

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
