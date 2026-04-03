"""
Lich map support.

Uses the local GSIV Lich map JSON as the authoritative world identity/wayto
source for room metadata and normal exits.  Local Lua/DB data is still allowed
to add custom special exits or hidden mechanics, but room naming and the common
travel graph should come from the Lich map instead of stale DB imports.
"""

from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from typing import Dict, Iterable, Optional

log = logging.getLogger(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MAP_JSON_PATH = os.path.join(PROJECT_ROOT, "map-1773601222.json")

_MOVE_RE = re.compile(r"""move\s*\(?\s*["']([^"'#{}][^"']*)["']""", re.IGNORECASE)
_FPUT_RE = re.compile(r"""fput\s+["']([^"'#{}][^"']*)["']""", re.IGNORECASE)
_DOTHIS_RE = re.compile(r"""dothistimeout\s*\(\s*["']([^"'#{}][^"']*)["']""", re.IGNORECASE)
_MULTIFPUT_RE = re.compile(r"""multifput\s+['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]""", re.IGNORECASE)
_SEARCH_RE = re.compile(r"""search(?:\s+[a-z][a-z _-]*)?""", re.IGNORECASE)

_NUISANCE_COMMANDS = {"hide", "unhide", "stand", "sit", "kneel"}
_GENERIC_GO_VERBS = {
    "go", "enter", "exit", "leave", "open", "close", "pull", "push", "turn",
    "cross", "board", "step", "crawl", "walk", "pass", "touch", "press", "ring",
    "raise", "lower", "jump", "duck", "slip", "twist", "run", "squeeze",
}

_DIRECTION_ALIASES = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
    "u": "up", "d": "down", "in": "in", "out": "out",
}

_RECIPROCAL_COMPASS = {
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

_PRESERVED_LOCAL_SPECIAL_EXITS = {
    # Ta'Vaalor rogue guild entry: keep the local shed access even when the
    # Lich wayto script for room 3509 is too complex to yield a clean exit.
    3509: {"go_shed"},
}


def _normalize_exit_key(direction: str) -> str:
    if direction is None:
        return ""
    normalized = str(direction).strip().lower().replace("-", "_")
    normalized = "_".join(normalized.split())
    return _DIRECTION_ALIASES.get(normalized, normalized)


def _normalize_command_to_exit_key(command: str) -> str:
    command = str(command or "").strip().lower()
    if not command:
        return ""

    parts = command.split()
    head = parts[0]
    tail = " ".join(parts[1:]).strip()

    if command == "search":
        return "search"
    if head == "search" and tail:
        return "search_" + _normalize_exit_key(tail)
    if head == "climb" and tail:
        return "climb_" + _normalize_exit_key(tail)
    if head == "swim" and tail:
        return "swim_" + _normalize_exit_key(tail)
    if head == "go" and tail:
        return "go_" + _normalize_exit_key(tail)
    if head in _GENERIC_GO_VERBS and tail:
        return "go_" + _normalize_exit_key(tail)
    if head in _DIRECTION_ALIASES or command in _DIRECTION_ALIASES:
        return _normalize_exit_key(command)
    if len(parts) == 1:
        return _normalize_exit_key(command)
    return ""


def _display_name(exit_key: str) -> str:
    key = _normalize_exit_key(exit_key)
    for prefix in ("go_", "climb_", "swim_", "search_"):
        if key.startswith(prefix):
            return key[len(prefix):].replace("_", " ")
    return key.replace("_", " ")


def _extract_title_text(entry: dict) -> str:
    raw = entry.get("title")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""
    text = str(raw or "").strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    return text


def _extract_description_text(entry: dict) -> str:
    raw = entry.get("description")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""
    return str(raw or "").strip()


def _split_title(title_text: str, fallback_zone: str = "") -> tuple[str, str]:
    text = str(title_text or "").strip()
    if not text:
        return str(fallback_zone or "").strip(), ""
    if "," in text:
        zone_text, room_text = text.split(",", 1)
        return zone_text.strip(), room_text.strip()
    return str(fallback_zone or "").strip(), text


def _parse_visible_paths(raw_paths: object) -> list[str]:
    values = raw_paths if isinstance(raw_paths, list) else [raw_paths]
    tokens: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        if ":" in text:
            text = text.split(":", 1)[1].strip()
        for part in text.split(","):
            key = _normalize_command_to_exit_key(part)
            if not key:
                continue
            if key.startswith("go_"):
                key = key[3:]
            if key not in seen:
                seen.add(key)
                tokens.append(key)
    return tokens


def build_lich_room_snapshot(entry: dict) -> dict:
    title_text = _extract_title_text(entry)
    description_text = _extract_description_text(entry)
    location_text = str(entry.get("location") or "").strip()
    path_values = entry.get("paths") or []
    if isinstance(path_values, list):
        paths_text = str(path_values[0] or "").strip() if path_values else ""
    else:
        paths_text = str(path_values or "").strip()
    uid_values = entry.get("uid") or []
    lich_uid = 0
    try:
        if isinstance(uid_values, list) and uid_values:
            lich_uid = int(uid_values[-1])
    except Exception:
        lich_uid = 0
    tags = [str(tag) for tag in (entry.get("tags") or []) if str(tag).strip()]
    return {
        "title": title_text,
        "location_name": location_text,
        "description": description_text,
        "paths_text": paths_text,
        "lich_uid": lich_uid,
        "tags": tags,
    }


def build_lich_exit_rows(entry: dict) -> list[dict]:
    rows: list[dict] = []
    for edge in _iter_wayto_edges(entry):
        exit_key = str(edge["exit_key"])
        target_room_id = int(edge["target_room_id"])
        hidden = bool(edge.get("hidden"))
        exit_verb = None
        is_special = 0
        search_dc = 0
        if exit_key.startswith("go_"):
            exit_verb = "go"
            is_special = 1
        elif exit_key.startswith("climb_"):
            exit_verb = "climb"
            is_special = 1
        elif exit_key.startswith("swim_"):
            exit_verb = "swim"
            is_special = 1
        elif exit_key.startswith("search_"):
            exit_verb = "search"
            is_special = 1
            hidden = True
            search_dc = 20
        rows.append({
            "direction": exit_key,
            "target_room_id": target_room_id,
            "exit_verb": exit_verb,
            "is_hidden": 1 if hidden else 0,
            "is_special": 1 if is_special or hidden else 0,
            "search_dc": search_dc,
        })
    rows.sort(key=lambda row: row["direction"])
    return rows


def _extract_command(raw: object) -> Optional[str]:
    command = str(raw or "").strip()
    if not command:
        return None

    if not command.startswith(";"):
        return command

    candidates: list[str] = []
    for pattern in (_MOVE_RE, _FPUT_RE, _DOTHIS_RE):
        for match in pattern.finditer(command):
            extracted = match.group(1).strip()
            if extracted:
                candidates.append(extracted)

    for extracted in reversed(candidates):
        if extracted.lower() not in _NUISANCE_COMMANDS:
            return extracted
    if candidates:
        return candidates[-1]
    return None


def _parse_hidden_wayto(command: str) -> Optional[dict]:
    text = str(command or "")
    lowered = text.lower()
    if "search" not in lowered:
        return None

    multifput_match = _MULTIFPUT_RE.search(text)
    if multifput_match:
        first = multifput_match.group(1).strip().lower()
        second = multifput_match.group(2).strip()
        if first.startswith("search"):
            move_key = _normalize_command_to_exit_key(second)
            if move_key and not move_key.startswith("search"):
                return {
                    "search_key": _normalize_command_to_exit_key(first),
                    "exit_key": move_key,
                }

    extracted = _extract_command(text)
    if not extracted:
        return None

    search_matches = _SEARCH_RE.findall(lowered)
    if not search_matches:
        return None

    move_key = _normalize_command_to_exit_key(extracted)
    if not move_key or move_key.startswith("search"):
        return None

    return {
        "search_key": _normalize_command_to_exit_key(search_matches[0]),
        "exit_key": move_key,
    }


@lru_cache(maxsize=1)
def _load_wayto_index() -> Dict[int, dict]:
    if not os.path.exists(MAP_JSON_PATH):
        log.warning("Lich map JSON not found at %s", MAP_JSON_PATH)
        return {}

    try:
        with open(MAP_JSON_PATH, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception as exc:
        log.error("Failed loading Lich map JSON %s: %s", MAP_JSON_PATH, exc)
        return {}

    rooms: Dict[int, dict] = {}
    iterable: Iterable[dict]
    if isinstance(payload, list):
        iterable = payload
    elif isinstance(payload, dict):
        iterable = payload.values()
    else:
        return {}

    for entry in iterable:
        if not isinstance(entry, dict):
            continue
        try:
            room_id = int(entry.get("id"))
        except Exception:
            continue
        rooms[room_id] = entry

    return rooms


def get_lich_room_entry(room_id: int) -> Optional[dict]:
    try:
        rid = int(room_id or 0)
    except Exception:
        rid = 0
    if rid <= 0:
        return None
    return _load_wayto_index().get(rid)


def _iter_wayto_edges(entry: dict):
    wayto = entry.get("wayto") or {}
    if not isinstance(wayto, dict):
        return

    for dest_str, raw_command in wayto.items():
        try:
            dest_room_id = int(dest_str)
        except Exception:
            continue

        command = str(raw_command or "").strip()
        if not command:
            continue

        hidden = _parse_hidden_wayto(command)
        if hidden:
            yield {
                "target_room_id": dest_room_id,
                "hidden": True,
                "search_key": hidden["search_key"],
                "exit_key": hidden["exit_key"],
                "command": command,
            }
            continue

        extracted = _extract_command(command)
        if not extracted:
            continue

        exit_key = _normalize_command_to_exit_key(extracted)
        if not exit_key or exit_key.startswith("search"):
            continue
        if len(exit_key) > 32:
            continue

        yield {
            "target_room_id": dest_room_id,
            "hidden": False,
            "exit_key": exit_key,
            "command": extracted,
        }


def _apply_lich_metadata(room, entry: dict) -> None:
    title_text = _extract_title_text(entry)
    location_text = str(entry.get("location") or "").strip()
    zone_name, room_name = _split_title(title_text, location_text)

    room.zone_name = zone_name or getattr(room, "zone_name", "") or location_text or getattr(getattr(room, "zone", None), "name", "") or ""
    if room_name:
        room.location_name = room_name
        room.title = room_name

    description_text = _extract_description_text(entry)
    if description_text:
        room.description = description_text

    try:
        uid_values = entry.get("uid") or []
        if isinstance(uid_values, list) and uid_values:
            room.lich_uid = int(uid_values[-1])
    except Exception:
        pass

    room.visible_path_hints = _parse_visible_paths(entry.get("paths"))

    tags = [str(tag).strip().lower() for tag in (entry.get("tags") or []) if str(tag).strip()]
    if tags:
        merged = list(dict.fromkeys([*(getattr(room, "tags", []) or []), *tags]))
        room.tags = merged


def enrich_room_from_lich_wayto(room, *, skip_exit_sync: bool = False) -> None:
    """
    Apply Lich-derived metadata and exit overlays to a room.

    Metadata sync always runs. Exit sync can be skipped for rooms whose movement
    is driven by another live system (for example ferries).
    """
    entry = get_lich_room_entry(int(getattr(room, "id", 0) or 0))

    room.lich_exit_aliases = {}
    room.lich_preferred_exit_names = {}
    room.local_exits = dict(getattr(room, "exits", {}) or {})
    room.visible_path_hints = list(getattr(room, "visible_path_hints", []) or [])
    room.zone_name = getattr(room, "zone_name", "") or getattr(getattr(room, "zone", None), "name", "") or ""

    if not entry:
        return

    _apply_lich_metadata(room, entry)

    if skip_exit_sync:
        return

    hidden_exits: Dict[str, dict] = {}
    authoritative_exits: Dict[str, int] = {}

    for edge in _iter_wayto_edges(entry):
        target_room_id = int(edge["target_room_id"])
        exit_key = str(edge["exit_key"])

        if edge.get("hidden"):
            if exit_key not in hidden_exits:
                hidden_exits[exit_key] = {
                    "target_room_id": target_room_id,
                    "search_dc": 20,
                    "exit_verb": exit_key.split("_", 1)[0] if "_" in exit_key else "go",
                    "message": f"Your careful search reveals a hidden path: {_display_name(exit_key)}",
                    "search_trigger": edge.get("search_key") or "search",
                    "source": "lich_wayto",
                }
            continue

        authoritative_exits[exit_key] = target_room_id
        room.lich_exit_aliases[exit_key] = target_room_id
        room.lich_preferred_exit_names[target_room_id] = exit_key

    room_id = int(getattr(room, "id", 0) or 0)
    for exit_key in _PRESERVED_LOCAL_SPECIAL_EXITS.get(room_id, set()):
        target_room_id = room.local_exits.get(exit_key)
        if target_room_id is None or exit_key in authoritative_exits:
            continue
        authoritative_exits[exit_key] = target_room_id

    room.exits = authoritative_exits
    room.hidden_exits = hidden_exits


def apply_reciprocal_compass_sync(rooms: Iterable, *, skip_room_ids: Optional[set[int]] = None) -> int:
    skip_room_ids = {int(rid) for rid in (skip_room_ids or set())}
    incoming: Dict[int, list[tuple[int, str]]] = {}
    changes = 0

    for room in rooms:
        room_id = int(getattr(room, "id", 0) or 0)
        if room_id in skip_room_ids:
            continue
        for key, target in (getattr(room, "exits", {}) or {}).items():
            normalized_key = _normalize_exit_key(key)
            reciprocal = _RECIPROCAL_COMPASS.get(normalized_key)
            if not reciprocal:
                continue
            try:
                target_id = int(target)
            except Exception:
                continue
            incoming.setdefault(target_id, []).append((room_id, normalized_key))

    for room in rooms:
        room_id = int(getattr(room, "id", 0) or 0)
        if room_id in skip_room_ids:
            continue
        visible_hints = set(getattr(room, "visible_path_hints", []) or [])
        if not visible_hints:
            continue

        exits = dict(getattr(room, "exits", {}) or {})
        aliases = dict(getattr(room, "lich_exit_aliases", {}) or {})
        for source_room_id, source_key in incoming.get(room_id, []):
            reverse_key = _RECIPROCAL_COMPASS.get(source_key)
            if not reverse_key or reverse_key not in visible_hints:
                continue
            if reverse_key in exits or reverse_key in aliases:
                continue
            exits[reverse_key] = source_room_id
            aliases[reverse_key] = source_room_id
            changes += 1

        room.exits = exits
        room.lich_exit_aliases = aliases

    return changes


def sync_world_from_lich(world, *, skip_exit_room_ids: Optional[set[int]] = None) -> dict:
    """
    Re-apply Lich room metadata/exits across the full loaded world.

    This is the authoritative pass used after DB/Lua world load so stale import
    data does not keep breaking names, zone labels, and exits.
    """
    skip_exit_room_ids = {int(rid) for rid in (skip_exit_room_ids or set())}
    rooms = list(getattr(world, "_rooms", {}).values())
    entry_count = 0

    for room in rooms:
        room_id = int(getattr(room, "id", 0) or 0)
        entry = get_lich_room_entry(room_id)
        if entry:
            entry_count += 1
        enrich_room_from_lich_wayto(room, skip_exit_sync=room_id in skip_exit_room_ids)

    reciprocal_added = apply_reciprocal_compass_sync(rooms, skip_room_ids=skip_exit_room_ids)
    return {
        "rooms_considered": len(rooms),
        "lich_rooms": entry_count,
        "reciprocal_added": reciprocal_added,
        "skip_exit_rooms": len(skip_exit_room_ids),
    }
