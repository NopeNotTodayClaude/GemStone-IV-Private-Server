"""
Trail tracking support for the TRACK command.

Stores recent departures from rooms so ranger tracking can follow fresh trails
using real movement data from players, NPCs, and creatures.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict, Iterable, List, Optional


_MAX_TRAILS_PER_ROOM = 64


@dataclass
class TrailRecord:
    actor_kind: str
    actor_id: int
    actor_name: str
    from_room_id: int
    to_room_id: int
    direction: str
    created_at: float
    hidden: bool = False
    sneaking: bool = False
    actor_level: int = 1

    @property
    def normalized_name(self) -> str:
        return (self.actor_name or "").strip().lower()


class TrailTracker:
    def __init__(self, server):
        self.server = server
        self._room_trails: Dict[int, Deque[TrailRecord]] = defaultdict(
            lambda: deque(maxlen=_MAX_TRAILS_PER_ROOM)
        )

    def record_departure(
        self,
        *,
        actor_kind: str,
        actor_id: int,
        actor_name: str,
        from_room_id: int,
        to_room_id: int,
        direction: Optional[str] = None,
        hidden: bool = False,
        sneaking: bool = False,
        actor_level: int = 1,
    ) -> None:
        if not from_room_id or not to_room_id or from_room_id == to_room_id:
            return

        if not direction:
            try:
                direction = self.server.world.get_direction_between(from_room_id, to_room_id)
            except Exception:
                direction = "out"

        record = TrailRecord(
            actor_kind=str(actor_kind or "unknown"),
            actor_id=int(actor_id or 0),
            actor_name=str(actor_name or "someone"),
            from_room_id=int(from_room_id),
            to_room_id=int(to_room_id),
            direction=str(direction or "out"),
            created_at=time.time(),
            hidden=bool(hidden),
            sneaking=bool(sneaking),
            actor_level=max(1, int(actor_level or 1)),
        )
        self._room_trails[int(from_room_id)].append(record)

    def trails_in_room(
        self,
        room_id: int,
        *,
        max_age: float = 900.0,
        name_query: Optional[str] = None,
    ) -> List[TrailRecord]:
        now = time.time()
        query = (name_query or "").strip().lower()
        trails: Iterable[TrailRecord] = self._room_trails.get(int(room_id), ())
        results: List[TrailRecord] = []
        for record in reversed(list(trails)):
            if (now - record.created_at) > max_age:
                continue
            if query and query not in record.normalized_name:
                continue
            results.append(record)
        return results
