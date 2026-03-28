"""
Room - Represents a single room in the game world.
"""

import json
import os
import logging
from typing import Dict, Optional, List

from server.core.world.lich_wayto import enrich_room_from_lich_wayto

log = logging.getLogger(__name__)

# Direction aliases for player convenience
DIRECTION_ALIASES = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
    "u": "up", "d": "down",
    "out": "out",
}

COMPASS_DIRECTIONS = [
    "north", "northeast", "east", "southeast",
    "south", "southwest", "west", "northwest",
    "up", "down", "out"
]


def normalize_exit_key(direction: str) -> str:
    """Normalize player-entered exit text to the DB/runtime key format."""
    if direction is None:
        return ""
    normalized = str(direction).strip().lower().replace("-", "_")
    normalized = "_".join(normalized.split())
    return DIRECTION_ALIASES.get(normalized, normalized)


class Room:
    """A single room in the game world."""

    def __init__(self):
        self.id = 0
        self.zone_id = 0
        self.zone = None
        self.lich_uid = 0
        self.title = "An Unknown Room"
        self.location_name = ""   # sub-location label (e.g. "Victory Road")
        self.description = "You see nothing of interest."
        self.exits: Dict[str, int] = {}         # direction -> room_id (all exits, incl. special)
        self.hidden_exits: Dict[str, dict] = {} # kept for compat, not used for display
        self.indoor = False
        self.dark = False
        self.safe = False
        self.supernode = False
        self.climbable = False
        self.terrain_type = ""
        self.climate = ""
        self.terrain = ""
        self.tags: List[str] = []
        self.objects: List[dict] = []
        self.lich_exit_aliases: Dict[str, int] = {}
        self.lich_preferred_exit_names: Dict[int, str] = {}

    @classmethod
    def from_db_row(cls, row: dict, zone) -> 'Room':
        """Construct a Room from a database row (rooms table)."""
        room = cls()
        room.id            = int(row["id"])
        room.zone_id       = int(row["zone_id"])
        room.zone          = zone
        room.lich_uid      = int(row.get("lich_uid") or 0)
        room.title         = row.get("title") or "An Unknown Room"
        room.location_name = row.get("location_name") or room.title
        room.description   = row.get("description") or "You see nothing of interest."
        room.safe          = bool(row.get("is_safe",      False))
        room.supernode     = bool(row.get("is_supernode", False))
        room.terrain_type  = row.get("terrain_type") or ""
        room.climate       = row.get("climate") or ""
        room.terrain       = row.get("terrain") or room.terrain_type
        # schema has both 'indoor' (migration) and 'is_indoor' (original) — handle both
        room.indoor        = bool(row.get("indoor") or row.get("is_indoor") or False)
        room.dark          = False
        room.climbable     = False
        room.exits         = {}   # populated separately from room_exits table
        tags_raw = row.get("tags_json")
        if isinstance(tags_raw, list):
            room.tags = [str(tag) for tag in tags_raw if tag is not None]
        elif isinstance(tags_raw, str) and tags_raw.strip():
            try:
                parsed = json.loads(tags_raw)
                if isinstance(parsed, list):
                    room.tags = [str(tag) for tag in parsed if tag is not None]
            except Exception:
                room.tags = []
        enrich_room_from_lich_wayto(room)
        return room

    @classmethod
    def load_from_lua(cls, filepath, zone):
        """Load a room from a Lua file."""
        room = cls()
        room.zone = zone
        room.zone_id = zone.id

        data = cls._parse_room_lua(filepath)

        room.id = data.get("id", 0)
        room.title = data.get("title", "An Unknown Room")
        room.description = data.get("description", "You see nothing of interest.")
        room.indoor = data.get("indoor", zone.indoor)
        room.dark = data.get("dark", False)
        room.safe = data.get("safe", False)
        room.supernode = data.get("supernode", False)
        room.climbable = data.get("climbable", False)

        # Parse exits
        room.exits = data.get("_exits", {})

        # Parse hidden exits (require SEARCH + Perception check to reveal)
        # Stored as { direction: { target_room_id, search_dc, exit_verb, message } }
        room.hidden_exits = data.get("_hidden_exits", {})

        # Runtime set: directions revealed to specific sessions this server session
        # { direction: set(character_id) }  — populated by cmd_search
        room._revealed_hidden_exits = {}
        enrich_room_from_lich_wayto(room)

        if room.id == 0:
            log.warning("Room in %s has id=0, may be template", filepath)

        return room

    @staticmethod
    def _parse_room_lua(filepath):
        """Parse room Lua file. Extracts properties and exit tables."""
        data = {}
        exits = {}
        hidden_exits = {}
        in_exits_block = False
        in_hidden_exits_block = False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    if not line or line.startswith("--"):
                        continue

                    # Detect hidden_exits block (must check before exits block)
                    if "Room.hidden_exits" in line and "{" in line:
                        in_hidden_exits_block = True
                        continue

                    if in_hidden_exits_block:
                        if "}" in line and "=" not in line:
                            in_hidden_exits_block = False
                            continue
                        # Parse: direction = { room_id = X, search_dc = Y, message = "..." }
                        # We only need the outer key and room_id/search_dc values
                        if "=" in line and "{" in line:
                            outer_key = line.split("=", 1)[0].strip()
                            room_id_m = __import__("re").search(r"room_id\s*=\s*(\d+)", line)
                            dc_m      = __import__("re").search(r"search_dc\s*=\s*(\d+)", line)
                            msg_m     = __import__("re").search(r'message\s*=\s*"([^"]+)"', line)
                            if outer_key and room_id_m:
                                hidden_exits[outer_key] = {
                                    "target_room_id": int(room_id_m.group(1)),
                                    "search_dc":      int(dc_m.group(1)) if dc_m else 20,
                                    "exit_verb":      "go",
                                    "message":        msg_m.group(1) if msg_m else None,
                                }
                        continue

                    # Detect exits block
                    if "Room.exits" in line and "{" in line:
                        in_exits_block = True
                        continue

                    if in_exits_block:
                        if "}" in line:
                            in_exits_block = False
                            continue
                        # Parse: direction = room_id,
                        if "=" in line:
                            parts = line.split("=", 1)
                            direction = parts[0].strip().strip(",")
                            room_id_str = parts[1].strip().rstrip(",")
                            try:
                                exits[direction] = int(room_id_str)
                            except ValueError:
                                pass
                        continue

                    # Regular property parsing
                    if "=" in line and not line.startswith("local") \
                            and not line.startswith("function") \
                            and not line.startswith("return"):
                        parts = line.split("=", 1)
                        key_part = parts[0].strip()
                        val_part = parts[1].strip().rstrip(",")

                        if "." in key_part:
                            key = key_part.split(".", 1)[1].strip()
                        else:
                            continue

                        if val_part.startswith('"') and val_part.endswith('"'):
                            data[key] = val_part.strip('"')
                        elif val_part.startswith("'") and val_part.endswith("'"):
                            data[key] = val_part.strip("'")
                        elif val_part.lower() == "true":
                            data[key] = True
                        elif val_part.lower() == "false":
                            data[key] = False
                        elif val_part.isdigit():
                            data[key] = int(val_part)

        except Exception as e:
            log.error("Error parsing room %s: %s", filepath, e)

        data["_exits"] = exits
        data["_hidden_exits"] = hidden_exits
        return data

    def format_look(self, session=None):
        """Format the room for the LOOK command output."""
        lines = []
        lines.append(f"[{self.title}]")
        lines.append(self.description)

        # Show other players
        if session:
            others = self.get_other_players(session)
            if others:
                names = ", ".join(s.character_name for s in others)
                if len(others) == 1:
                    lines.append(f"You also see {names}.")
                else:
                    lines.append(f"Also here: {names}.")

        # Show exits — include any hidden exits this session has revealed
        exit_type = "Obvious exits" if self.indoor else "Obvious paths"
        all_exit_names = self.get_display_exit_names(session)

        if all_exit_names:
            lines.append(f"{exit_type}: {', '.join(all_exit_names)}")
        else:
            lines.append(f"{exit_type}: none")

        return "\r\n".join(lines)

    def get_exit(self, direction: str) -> Optional[int]:
        """Get the room ID for a given exit direction (normal exits only)."""
        direction = normalize_exit_key(direction)
        if not direction:
            return None
        if direction in self.exits:
            return self.exits[direction]
        go_key = f"go_{direction}"
        if go_key in self.exits:
            return self.exits[go_key]
        if direction in self.lich_exit_aliases:
            return self.lich_exit_aliases[direction]
        if go_key in self.lich_exit_aliases:
            return self.lich_exit_aliases[go_key]
        return None

    @staticmethod
    def _exit_aliases(exit_key: str) -> List[str]:
        """Return accepted aliases for an exit key, from exact to shorthand."""
        normalized = normalize_exit_key(exit_key)
        if not normalized:
            return []

        aliases: List[str] = [normalized]
        base = normalized

        if "_" in normalized:
            first, rest = normalized.split("_", 1)
            if first in {"go", "climb", "swim"} and rest:
                base = rest
                aliases.append(rest)

        if "_" in base:
            aliases.append(base.split("_")[-1])

        seen = set()
        ordered: List[str] = []
        for alias in aliases:
            if alias and alias not in seen:
                ordered.append(alias)
                seen.add(alias)
        return ordered

    @staticmethod
    def display_exit_name(exit_key: str) -> str:
        """Convert runtime exit keys to human-readable room text."""
        normalized = normalize_exit_key(exit_key)
        for prefix in ("go_", "climb_", "swim_"):
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break
        return normalized.replace("_", " ")

    def get_display_exit_names(self, session=None) -> List[str]:
        """Return visible exit labels, preferring Lich labels for mismatched rooms."""
        target_to_keys: Dict[int, List[str]] = {}
        for key, target in self.exits.items():
            target_to_keys.setdefault(target, []).append(key)

        visible_keys: List[str] = []
        for target_room_id, local_keys in target_to_keys.items():
            has_local_special = any(
                key.startswith(("go_", "climb_", "swim_"))
                for key in local_keys
            )
            preferred = self.lich_preferred_exit_names.get(target_room_id)
            if preferred and not has_local_special:
                visible_keys.append(preferred)
            else:
                visible_keys.extend(local_keys)

        for alias_key, target_room_id in self.lich_exit_aliases.items():
            if target_room_id not in target_to_keys:
                visible_keys.append(alias_key)

        display_names = [self.display_exit_name(key) for key in visible_keys]

        if session:
            visible_hidden = self.get_visible_hidden_exits(session)
            for key in sorted(visible_hidden.keys()):
                display_names.append(self.display_exit_name(key) + " (hidden path)")
            server = getattr(session, "server", None)
            pets = getattr(server, "pets", None) if server else None
            if pets:
                for key in sorted((pets.get_dynamic_room_exits(session, self) or {}).keys()):
                    display_names.append(self.display_exit_name(key) + " (hidden path)")

        seen = set()
        ordered: List[str] = []
        for name in sorted(display_names):
            if name and name not in seen:
                ordered.append(name)
                seen.add(name)
        return ordered

    def find_exit_matches(self, direction: str, session=None) -> Dict[str, int]:
        """
        Return all exits matching the player's input, including revealed
        hidden exits for the provided session.
        """
        direction = normalize_exit_key(direction)
        if not direction:
            return {}

        matches: Dict[str, int] = {}
        for key, target_id in self.exits.items():
            if direction in self._exit_aliases(key):
                matches[key] = target_id

        for key, target_id in self.lich_exit_aliases.items():
            if direction in self._exit_aliases(key):
                matches.setdefault(key, target_id)

        if session:
            char_id = getattr(session, "character_id", None)
            if char_id is not None:
                revealed = getattr(self, "_revealed_hidden_exits", {})
                for key, he in self.hidden_exits.items():
                    if char_id not in revealed.get(key, set()):
                        continue
                    if direction in self._exit_aliases(key):
                        matches[key] = he["target_room_id"]
            server = getattr(session, "server", None)
            pets = getattr(server, "pets", None) if server else None
            if pets:
                for key, target_id in (pets.get_dynamic_room_exits(session, self) or {}).items():
                    if direction in self._exit_aliases(key):
                        matches[key] = target_id

        return matches

    def get_exit_for_session(self, direction: str, session) -> Optional[int]:
        """
        Get the room ID for a direction, including any hidden exits that
        this session has revealed via SEARCH.
        Use this in movement.py instead of get_exit when handling GO commands.
        """
        # Normal exits first
        result = self.get_exit(direction)
        if result is not None:
            return result

        # Check hidden exits this session has revealed
        char_id = getattr(session, "character_id", None)
        if char_id is None:
            return None

        revealed = getattr(self, "_revealed_hidden_exits", {})
        direction_lower = normalize_exit_key(direction)
        if not direction_lower:
            return None

        for key, he in self.hidden_exits.items():
            key_lower = normalize_exit_key(key)
            match_keys = {key_lower}
            if "_" in key_lower:
                match_keys.add(key_lower.split("_", 1)[1])
            if direction_lower in match_keys:
                if char_id in revealed.get(key, set()):
                    return he["target_room_id"]

        server = getattr(session, "server", None)
        pets = getattr(server, "pets", None) if server else None
        if pets:
            for key, target_id in (pets.get_dynamic_room_exits(session, self) or {}).items():
                key_lower = normalize_exit_key(key)
                match_keys = {key_lower}
                if "_" in key_lower:
                    match_keys.add(key_lower.split("_", 1)[1])
                if direction_lower in match_keys:
                    return target_id

        return None

    def reveal_hidden_exit(self, direction_key: str, session) -> bool:
        """
        Mark a hidden exit as revealed for this session's character.
        Returns True if it was newly revealed, False if already known.
        """
        char_id = getattr(session, "character_id", None)
        if char_id is None:
            return False
        if not hasattr(self, "_revealed_hidden_exits"):
            self._revealed_hidden_exits = {}
        if direction_key not in self._revealed_hidden_exits:
            self._revealed_hidden_exits[direction_key] = set()
        if char_id in self._revealed_hidden_exits[direction_key]:
            return False
        self._revealed_hidden_exits[direction_key].add(char_id)
        return True

    def get_visible_hidden_exits(self, session) -> dict:
        """
        Return the subset of hidden_exits this session has revealed.
        Used by format_look to append revealed hidden paths to the exit list.
        """
        char_id = getattr(session, "character_id", None)
        if char_id is None:
            return {}
        revealed = getattr(self, "_revealed_hidden_exits", {})
        return {
            key: he for key, he in self.hidden_exits.items()
            if char_id in revealed.get(key, set())
        }

    def get_other_players(self, exclude_session):
        """Get other players in this room."""
        all_players = self.zone.rooms  # This needs world manager reference
        # Will be properly wired through world manager
        return []

    def __repr__(self):
        return f"Room({self.id}, '{self.title}')"
