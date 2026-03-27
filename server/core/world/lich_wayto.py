"""
Lich map wayto support.

Uses the GSIV Lich map JSON as a data-driven alias layer so the live server can
accept the same exit labels the client/go2/path graph uses, without rewriting
thousands of room Lua files by hand.
"""

from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from typing import Dict, Optional

log = logging.getLogger(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MAP_JSON_PATH = os.path.join(PROJECT_ROOT, "map-1773601222.json")

_MOVE_RE = re.compile(r"""move\s*\(?\s*['"]([^'"]+)['"]""", re.IGNORECASE)
_MULTIFPUT_RE = re.compile(r"""multifput\s+['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]""", re.IGNORECASE)
_SEARCH_RE = re.compile(r"""search(?:\s+[a-z][a-z _-]*)?""", re.IGNORECASE)

_DIRECTION_ALIASES = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
    "u": "up", "d": "down",
    "out": "out",
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

    if command.startswith("go "):
        return "go_" + _normalize_exit_key(command[3:])
    if command.startswith("climb "):
        return "climb_" + _normalize_exit_key(command[6:])
    if command.startswith("swim "):
        return "swim_" + _normalize_exit_key(command[5:])
    if command.startswith("search "):
        return "search_" + _normalize_exit_key(command[7:])
    if command == "search":
        return "search"
    return _normalize_exit_key(command)


def _display_name(exit_key: str) -> str:
    key = _normalize_exit_key(exit_key)
    for prefix in ("go_", "climb_", "swim_"):
        if key.startswith(prefix):
            return key[len(prefix):].replace("_", " ")
    return key.replace("_", " ")


def _is_simple_wayto(command: str) -> bool:
    text = str(command or "").strip()
    if not text:
        return False
    lowered = text.lower()
    if ";" in text or "\n" in text or "move " in lowered or "fput " in lowered or "waitrt" in lowered:
        return False
    return True


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
            if move_key:
                return {
                    "search_key": _normalize_command_to_exit_key(first),
                    "exit_key": move_key,
                }

    move_matches = _MOVE_RE.findall(text)
    if len(move_matches) != 1:
        return None

    search_matches = _SEARCH_RE.findall(lowered)
    if not search_matches:
        return None

    move_key = _normalize_command_to_exit_key(move_matches[0])
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


def enrich_room_from_lich_wayto(room) -> None:
    """
    Attach Lich-driven alias exits and simple hidden SEARCH exits to the room.

    This keeps local Lua/DB exits authoritative, but supplements them so the
    server accepts the same travel labels that Lich/go2 and the client graph use.
    """
    entry = _load_wayto_index().get(int(getattr(room, "id", 0) or 0))

    room.lich_exit_aliases = {}
    room.lich_preferred_exit_names = {}
    room.local_exits = dict(getattr(room, "exits", {}) or {})

    if not entry:
        return

    wayto = entry.get("wayto") or {}
    if not isinstance(wayto, dict):
        return

    local_by_target: Dict[int, list] = {}
    original_exits = dict(getattr(room, "exits", {}) or {})
    for key, target in original_exits.items():
        try:
            local_by_target.setdefault(int(target), []).append(str(key))
        except Exception:
            continue

    hidden_exits = getattr(room, "hidden_exits", {}) or {}
    authoritative_exits: Dict[str, int] = {}

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
            exit_key = hidden["exit_key"]
            if exit_key not in hidden_exits:
                hidden_exits[exit_key] = {
                    "target_room_id": dest_room_id,
                    "search_dc": 20,
                    "exit_verb": exit_key.split("_", 1)[0] if "_" in exit_key else "go",
                    "message": f"Your careful search reveals a hidden path: {_display_name(exit_key)}",
                    "search_trigger": hidden["search_key"] or "search",
                    "source": "lich_wayto",
                }
            continue

        if not _is_simple_wayto(command):
            continue

        alias_key = _normalize_command_to_exit_key(command)
        if not alias_key:
            continue

        authoritative_exits[alias_key] = dest_room_id
        room.lich_exit_aliases[alias_key] = dest_room_id

        local_keys = local_by_target.get(dest_room_id, [])
        has_local_special = any(
            key.startswith(("go_", "climb_", "swim_")) for key in local_keys
        )
        if alias_key.startswith(("go_", "climb_", "swim_")) and not has_local_special:
            room.lich_preferred_exit_names[dest_room_id] = alias_key

    if authoritative_exits:
        preserved_exits: Dict[str, int] = {}
        authoritative_targets = {int(target) for target in authoritative_exits.values()}
        for key, target in original_exits.items():
            normalized_key = _normalize_exit_key(key)
            if normalized_key in authoritative_exits:
                continue
            try:
                target_id = int(target)
            except Exception:
                continue
            if target_id in authoritative_targets:
                continue
            # Preserve local-only special exits that Lich does not model, but
            # drop stray compass/outdoor directions so bad legacy room files do
            # not override the authoritative wayto data.
            if "_" in normalized_key:
                preserved_exits[normalized_key] = target_id
        room.exits = {**authoritative_exits, **preserved_exits}

    room.hidden_exits = hidden_exits
