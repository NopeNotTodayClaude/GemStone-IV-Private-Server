"""
WorldManager - Loads and manages all zones, rooms, and the room graph.
Handles Lua script loading for zone/room definitions.
"""

import os
import logging
import time
from typing import Optional, Dict, List
from server.core.world.room import Room
from server.core.world.zone import Zone

log = logging.getLogger(__name__)


class WorldManager:
    """Manages the entire game world — zones, rooms, pathfinding."""

    def __init__(self, server):
        self.server = server
        self._zones: Dict[str, Zone] = {}
        self._rooms: Dict[int, Room] = {}
        self._room_players: Dict[int, List] = {}  # room_id -> [sessions]
        self._lua_room_ids: set[int] = set()

    async def initialize(self):
        """Load all zones and rooms from Lua scripts, then fill the rest from the database."""

        # ── Phase 1: Lua scripts (hand-crafted rooms with event hooks) ─────────
        scripts_path = self.server.config.get("paths.scripts", "./scripts")
        zones_path   = os.path.join(scripts_path, "zones")

        if os.path.exists(zones_path):
            for zone_dir_name in sorted(os.listdir(zones_path)):
                zone_path = os.path.join(zones_path, zone_dir_name)

                if zone_dir_name.startswith("_") or not os.path.isdir(zone_path):
                    continue

                zone_file = os.path.join(zone_path, "zone.lua")
                if not os.path.exists(zone_file):
                    log.warning("Zone directory '%s' has no zone.lua, skipping", zone_dir_name)
                    continue

                try:
                    zone = Zone.load_from_lua(zone_dir_name, zone_path)
                    self._zones[zone.slug] = zone

                    rooms_path = os.path.join(zone_path, "rooms")
                    if os.path.exists(rooms_path):
                        for room_file in sorted(os.listdir(rooms_path)):
                            if room_file.endswith(".lua"):
                                room_path = os.path.join(rooms_path, room_file)
                                try:
                                    room = Room.load_from_lua(room_path, zone)
                                    self._rooms[room.id] = room
                                    self._lua_room_ids.add(room.id)
                                    zone.rooms[room.id] = room
                                except Exception as e:
                                    log.error("Failed to load room %s: %s", room_path, e)

                    log.info("  Zone '%s' loaded (%d rooms from Lua)", zone.name, len(zone.rooms))

                except Exception as e:
                    log.error("Failed to load zone '%s': %s", zone_dir_name, e, exc_info=True)
        else:
            log.warning("Zones directory not found: %s", zones_path)

        lua_room_count = len(self._rooms)
        log.info("Lua load complete: %d zones, %d rooms", len(self._zones), lua_room_count)

        # ── Phase 2: Database rooms (the 33k+ rooms built by the team) ─────────
        await self._load_from_database()

        log.info(
            "World initialization complete: %d zones, %d rooms total "
            "(%d from Lua, %d from DB)",
            len(self._zones),
            len(self._rooms),
            lua_room_count,
            len(self._rooms) - lua_room_count,
        )

    async def _load_from_database(self):
        """
        Load all zones and rooms from the database that aren't already loaded
        from Lua scripts.  Lua definitions always take priority — DB rows for
        rooms already in self._rooms are skipped so scripted rooms keep their
        event hooks.

        Loads in three queries:
          1. All zones  (builds Zone objects for any not already Lua-loaded)
          2. All rooms  (skips IDs already in self._rooms)
          3. All exits  (room_exits table — attaches to every loaded room)
        """
        db = getattr(self.server, "db", None)
        if not db or not db._pool:
            log.warning("WorldManager: no DB connection — skipping database room load")
            return

        try:
            conn = db._get_conn()
        except Exception as e:
            log.error("WorldManager: could not get DB connection for world load: %s", e)
            return

        try:
            cur = conn.cursor(dictionary=True)

            # ── 1. Zones ───────────────────────────────────────────────────────
            cur.execute(
                "SELECT id, slug, name, region, level_min, level_max, climate "
                "FROM zones WHERE is_enabled = 1"
            )
            db_zones = cur.fetchall()
            zones_by_id: Dict[int, Zone] = {}

            for row in db_zones:
                zone_id = int(row["id"])
                slug    = row.get("slug", "")

                # Build a lookup by id for the room-loading phase
                # Use the Lua zone if we already have it (it may have a different slug key)
                existing = self._zones.get(slug) or self.get_zone_by_id(zone_id)
                if existing:
                    zones_by_id[zone_id] = existing
                else:
                    zone = Zone.from_db_row(row)
                    self._zones[zone.slug] = zone
                    zones_by_id[zone_id] = zone

            log.info("  DB zones resolved: %d total (%d already from Lua)",
                     len(zones_by_id),
                     sum(1 for z in zones_by_id.values() if z.slug in self._zones))

            # ── 2. Rooms ───────────────────────────────────────────────────────
            # Pull every room column we care about in one shot.
            # COALESCE indoor / is_indoor handles both schema versions.
            cur.execute("""
                SELECT
                    id,
                    zone_id,
                    lich_uid,
                    title,
                    description,
                    location_name,
                    tags_json,
                    is_safe,
                    is_supernode,
                    terrain_type,
                    climate,
                    terrain,
                    COALESCE(indoor, is_indoor, 0) AS indoor
                FROM rooms
            """)

            skipped  = 0
            loaded   = 0
            orphaned = 0

            for row in cur.fetchall():
                room_id = int(row["id"])

                # Lua rooms win — never overwrite them
                if room_id in self._rooms:
                    skipped += 1
                    continue

                zone_id = int(row["zone_id"])
                zone    = zones_by_id.get(zone_id)
                if not zone:
                    orphaned += 1
                    continue

                room = Room.from_db_row(row, zone)
                self._rooms[room_id] = room
                zone.rooms[room_id]  = room
                loaded += 1

            log.info(
                "  DB rooms: %d loaded, %d skipped (Lua override), %d orphaned (unknown zone)",
                loaded, skipped, orphaned
            )

            # ── 3. Exits ───────────────────────────────────────────────────────
            # One bulk fetch — attach to rooms already in self._rooms.
            # ALL exits go into room.exits regardless of is_hidden or is_special.
            # This is a single-player server — QOL over spoiler prevention.
            # exit_verb tells us what the player types (go, climb, swim etc).
            # We store direction key as "verb_target" so movement can resolve it.
            cur.execute("""
                SELECT room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc
                FROM room_exits
            """)

            exits_loaded  = 0
            exits_missing = 0
            exits_skipped = 0

            for row in cur.fetchall():
                room_id   = int(row["room_id"])
                target_id = int(row["target_room_id"])
                direction = row["direction"]   # e.g. "go_bridge", "north", "climb_staircase"

                room = self._rooms.get(room_id)
                if not room:
                    exits_missing += 1
                    continue

                if room_id in self._lua_room_ids:
                    exits_skipped += 1
                    continue

                # Every exit goes into room.exits — no gating on hidden/special
                room.exits[direction] = target_id
                exits_loaded += 1

            log.info(
                "  DB exits: %d loaded, %d skipped (Lua room override), %d skipped (room not in world)",
                exits_loaded, exits_skipped, exits_missing
            )

        except Exception as e:
            log.error("WorldManager: DB load failed: %s", e, exc_info=True)
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

    def get_room(self, room_id: int) -> Optional[Room]:
        return self._rooms.get(room_id)

    def get_ground_items(self, room_id: int, refresh: bool = False) -> list:
        """Return persisted ground items for a room, purging expired trash first."""
        room = self.get_room(room_id)
        if not room:
            return []

        if getattr(self.server, "db", None):
            try:
                items = self.server.db.get_room_ground_items(room_id)
            except Exception as e:
                log.error("Failed loading ground items for room %s: %s", room_id, e)
                items = list(getattr(room, "_ground_items", []))
            room._ground_items = items
            return items

        # DB-less fallback for development mode
        items = list(getattr(room, "_ground_items", []))
        now = time.time()
        kept = []
        for item in items:
            expires_at = item.get("expires_at")
            if isinstance(expires_at, (int, float)) and expires_at <= now:
                continue
            kept.append(item)
        room._ground_items = kept
        return kept

    def add_ground_item(self, room_id: int, item: dict, *, dropped_by_character_id=None, dropped_by_name=None, source="drop"):
        """Persist an item on the ground and refresh the room cache."""
        room = self.get_room(room_id)
        if not room:
            return None

        snapshot = {
            key: value for key, value in dict(item or {}).items()
            if key not in {"inv_id", "slot", "container_id", "ground_id", "room_id"}
        }
        if getattr(self.server, "db", None):
            ground_id = self.server.db.save_ground_item(
                room_id,
                snapshot,
                dropped_by_character_id=dropped_by_character_id,
                dropped_by_name=dropped_by_name,
                source=source,
            )
            self.get_ground_items(room_id, refresh=True)
            return ground_id

        ttl = 3600 if int(snapshot.get("value") or 0) >= 5000 else 1800
        snapshot["expires_at"] = time.time() + ttl
        room._ground_items = getattr(room, "_ground_items", [])
        room._ground_items.append(snapshot)
        return None

    def remove_ground_item(self, room_id: int, ground_item) -> bool:
        """Remove a ground item from persistence/cache."""
        room = self.get_room(room_id)
        if not room:
            return False
        ground_id = None
        if isinstance(ground_item, dict):
            ground_id = ground_item.get("ground_id")
        elif ground_item is not None:
            ground_id = ground_item

        if getattr(self.server, "db", None) and ground_id:
            ok = self.server.db.remove_ground_item(ground_id)
            self.get_ground_items(room_id, refresh=True)
            return ok

        items = list(getattr(room, "_ground_items", []))
        for item in items:
            if item is ground_item or item.get("ground_id") == ground_id:
                items.remove(item)
                room._ground_items = items
                return True
        return False

    def cleanup_ground_items(self):
        """Purge expired ground trash globally and refresh loaded room caches."""
        if getattr(self.server, "db", None):
            removed = self.server.db.cleanup_expired_ground_items()
            if removed:
                for room in self._rooms.values():
                    if hasattr(room, "_ground_items"):
                        self.get_ground_items(room.id, refresh=True)
            return removed

        now = time.time()
        removed = 0
        for room in self._rooms.values():
            items = list(getattr(room, "_ground_items", []))
            kept = []
            for item in items:
                expires_at = item.get("expires_at")
                if isinstance(expires_at, (int, float)) and expires_at <= now:
                    removed += 1
                    continue
                kept.append(item)
            room._ground_items = kept
        return removed

    def get_zone(self, slug: str) -> Optional[Zone]:
        return self._zones.get(slug)

    def get_all_zones(self) -> list:
        """Return all loaded Zone objects."""
        return list(self._zones.values())

    def get_zone_by_id(self, zone_id: int) -> Optional[Zone]:
        """Find a Zone by its integer ID (Zone.id field)."""
        for zone in self._zones.values():
            if getattr(zone, "id", None) == zone_id:
                return zone
        return None

    def add_player_to_room(self, session, room_id: int):
        """Place a player session in a room."""
        if room_id not in self._room_players:
            self._room_players[room_id] = []
        if session not in self._room_players[room_id]:
            self._room_players[room_id].append(session)

    def remove_player_from_room(self, session, room_id: int):
        """Remove a player session from a room."""
        if room_id in self._room_players:
            if session in self._room_players[room_id]:
                self._room_players[room_id].remove(session)

    def get_players_in_room(self, room_id: int) -> List:
        """Get all player sessions in a given room."""
        return self._room_players.get(room_id, [])

    def get_all_players(self) -> List:
        """Get all active player sessions across all rooms."""
        return list(self.server.sessions._sessions.values())

    async def broadcast_to_room(self, room_id: int, message: str, exclude=None):
        """Send a message to all players in a room, optionally excluding one."""
        for session in self.get_players_in_room(room_id):
            if session != exclude:
                await session.send_line(message)

    @property
    def zone_count(self):
        return len(self._zones)

    @property
    def room_count(self):
        return len(self._rooms)

    def find_path(self, from_room_id: int, to_room_id: int) -> list:
        """
        BFS shortest path between two rooms.
        Returns list of room_ids from start to goal (inclusive),
        or empty list if no path exists.
        """
        if from_room_id == to_room_id:
            return [from_room_id]

        from collections import deque
        visited = {from_room_id}
        queue   = deque([[from_room_id]])

        while queue:
            path    = queue.popleft()
            current = path[-1]
            room    = self._rooms.get(current)
            if not room:
                continue
            for _, next_room_id in room.exits.items():
                if next_room_id not in visited:
                    new_path = path + [next_room_id]
                    if next_room_id == to_room_id:
                        return new_path
                    visited.add(next_room_id)
                    queue.append(new_path)

        return []

    def get_direction_between(self, from_room_id: int, to_room_id: int) -> str:
        """Return the exit direction name from from_room to to_room, or 'out' if unknown."""
        room = self._rooms.get(from_room_id)
        if not room:
            return "out"
        for direction, room_id in room.exits.items():
            if room_id == to_room_id:
                return direction
        return "out"
