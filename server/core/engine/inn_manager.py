"""
inn_manager.py
--------------
Lua-backed inn registry and runtime services.

Responsibilities:
  - CHECK IN / CHECK OUT / CHECK ROOM
  - private room + private table ownership
  - latch and invite handling
  - inn-aware TRAIN / FIXSTATS gating
  - movement access checks for rented private spaces
"""

from __future__ import annotations

import logging
from typing import Optional

from server.core.protocol.colors import npc_speech

log = logging.getLogger(__name__)


def _norm(text: str | None) -> str:
    return " ".join(str(text or "").strip().lower().replace("-", " ").replace("_", " ").split())


class InnManager:
    def __init__(self, server):
        self.server = server
        self._inns: dict[str, dict] = {}
        self._room_to_inn: dict[int, dict] = {}
        self._front_desks: dict[int, dict] = {}
        self._template_to_inn: dict[str, dict] = {}
        self._private_rooms: dict[int, dict] = {}
        self._private_tables: dict[int, dict] = {}
        self._stays_by_character: dict[int, dict] = {}
        self._occupied_rooms: dict[int, dict] = {}
        self._occupied_tables: dict[int, dict] = {}
        self._access_by_room: dict[int, set[int]] = {}

    async def initialize(self):
        data = getattr(self.server.lua, "get_inns", lambda: {})() or {}
        self._load_registry(data.get("inns") or {})
        self._reload_persistence()
        log.info("InnManager ready (%d inns, %d mapped rooms)", len(self._inns), len(self._room_to_inn))

    def _load_registry(self, inns: dict[str, dict]) -> None:
        self._inns = {}
        self._room_to_inn = {}
        self._front_desks = {}
        self._template_to_inn = {}
        self._private_rooms = {}
        self._private_tables = {}

        world_rooms = list(getattr(self.server.world, "_rooms", {}).values())

        for inn_id, raw in inns.items():
            front_desk_room_id = int(raw.get("front_desk_room_id") or 0)
            if front_desk_room_id <= 0:
                continue

            prefixes = [str(x).strip() for x in (raw.get("room_title_prefixes") or []) if str(x).strip()]
            location_names = {str(x).strip() for x in (raw.get("location_names") or []) if str(x).strip()}
            all_room_ids = set(int(x) for x in (raw.get("explicit_room_ids") or []) if int(x) > 0)
            rentable_room_ids = set(int(x) for x in (raw.get("rentable_room_ids") or []) if int(x) > 0)
            private_table_room_ids = set(int(x) for x in (raw.get("private_table_room_ids") or []) if int(x) > 0)

            for room in world_rooms:
                title = str(getattr(room, "title", "") or "")
                location = str(getattr(room, "location_name", "") or "")
                if any(title.startswith(prefix) for prefix in prefixes) or location in location_names:
                    all_room_ids.add(int(room.id))

            all_room_ids.add(front_desk_room_id)
            all_room_ids.update(rentable_room_ids)
            all_room_ids.update(private_table_room_ids)

            if raw.get("auto_latch_tag", True):
                for room_id in list(all_room_ids):
                    room = self.server.world.get_room(room_id)
                    if not room:
                        continue
                    if "meta:latched" in set(getattr(room, "tags", []) or []):
                        rentable_room_ids.add(room_id)
                        all_room_ids.add(room_id)

            inn = {
                "id": str(inn_id),
                "display_name": str(raw.get("display_name") or inn_id).strip(),
                "town_name": str(raw.get("town_name") or "").strip(),
                "front_desk_room_id": front_desk_room_id,
                "aliases": {_norm(alias) for alias in (raw.get("aliases") or []) if _norm(alias)},
                "all_room_ids": set(sorted(all_room_ids)),
                "rentable_room_ids": sorted(rentable_room_ids),
                "private_table_room_ids": sorted(private_table_room_ids),
            }
            inn["aliases"].add(_norm(inn["display_name"]))
            if inn["town_name"]:
                inn["aliases"].add(_norm(inn["town_name"]))

            self._inns[inn["id"]] = inn
            self._front_desks[front_desk_room_id] = inn
            for template_id in raw.get("innkeeper_template_ids") or []:
                tid = str(template_id or "").strip()
                if tid:
                    self._template_to_inn[tid] = inn
            for room_id in inn["all_room_ids"]:
                self._room_to_inn[room_id] = inn
            for room_id in inn["rentable_room_ids"]:
                self._private_rooms[room_id] = inn
            for room_id in inn["private_table_room_ids"]:
                self._private_tables[room_id] = inn

    def _reload_persistence(self) -> None:
        self._stays_by_character = {}
        self._occupied_rooms = {}
        self._occupied_tables = {}
        self._access_by_room = {}
        db = getattr(self.server, "db", None)
        if not db:
            return

        for row in db.load_character_inn_stays() or []:
            self._cache_stay(row)

        for row in db.load_character_inn_access() or []:
            room_id = int(row.get("room_id") or 0)
            guest_character_id = int(row.get("guest_character_id") or 0)
            if room_id > 0 and guest_character_id > 0:
                self._access_by_room.setdefault(room_id, set()).add(guest_character_id)

    def _cache_stay(self, row: dict | None) -> None:
        if not row:
            return
        character_id = int(row.get("character_id") or 0)
        if character_id <= 0:
            return
        stay = {
            "character_id": character_id,
            "inn_id": str(row.get("inn_id") or "").strip(),
            "checked_in_room_id": int(row.get("checked_in_room_id") or 0),
            "private_room_id": int(row.get("private_room_id") or 0),
            "private_table_room_id": int(row.get("private_table_room_id") or 0),
            "room_latched": bool(row.get("room_latched", False)),
        }
        self._stays_by_character[character_id] = stay
        if stay["private_room_id"] > 0:
            self._occupied_rooms[stay["private_room_id"]] = stay
        if stay["private_table_room_id"] > 0:
            self._occupied_tables[stay["private_table_room_id"]] = stay

    def _forget_stay(self, character_id: int) -> None:
        old = self._stays_by_character.pop(int(character_id or 0), None)
        if not old:
            return
        room_id = int(old.get("private_room_id") or 0)
        table_id = int(old.get("private_table_room_id") or 0)
        if room_id > 0:
            self._occupied_rooms.pop(room_id, None)
        if table_id > 0:
            self._occupied_tables.pop(table_id, None)

    def get_inn_for_room(self, room_id: int | None) -> Optional[dict]:
        try:
            return self._room_to_inn.get(int(room_id or 0))
        except Exception:
            return None

    def get_inn_for_npc(self, npc) -> Optional[dict]:
        template_id = str(getattr(npc, "template_id", "") or "").strip()
        if template_id and template_id in self._template_to_inn:
            return self._template_to_inn[template_id]
        room_id = int(getattr(npc, "room_id", 0) or getattr(npc, "home_room_id", 0) or 0)
        return self._front_desks.get(room_id) or self.get_inn_for_room(room_id)

    def get_stay(self, character_id: int | None) -> Optional[dict]:
        try:
            return self._stays_by_character.get(int(character_id or 0))
        except Exception:
            return None

    def is_inn_room(self, room_id: int | None) -> bool:
        return self.get_inn_for_room(room_id) is not None

    def can_use_character_manager(self, session) -> bool:
        room = getattr(session, "current_room", None)
        stay = self.get_stay(getattr(session, "character_id", 0))
        inn = self.get_inn_for_room(getattr(room, "id", 0) if room else 0)
        return bool(room and inn and stay and stay.get("inn_id") == inn["id"])

    def can_use_fixstats(self, session) -> bool:
        return self.can_use_character_manager(session)

    def training_gate_message(self) -> str:
        return "You must CHECK IN at an inn front desk before you can access the character manager here."

    def fixstats_gate_message(self) -> str:
        return "You must be checked in at an inn to reallocate your stats."

    async def check_in(self, session) -> bool:
        room = getattr(session, "current_room", None)
        inn = self._front_desks.get(int(getattr(room, "id", 0) or 0))
        if not inn:
            await session.send_line("You need to be standing at an inn front desk to CHECK IN.")
            return True

        stay = self.get_stay(session.character_id)
        if stay and stay.get("inn_id") == inn["id"]:
            await session.send_line(
                f"You are already checked in at {inn['display_name']}.  TRAIN and FIXSTATS are available while you remain here."
            )
            return True

        if stay:
            self._clear_stay(session.character_id)

        row = self.server.db.upsert_character_inn_stay(
            session.character_id,
            inn["id"],
            inn["front_desk_room_id"],
            private_room_id=None,
            private_table_room_id=None,
            room_latched=False,
        ) if getattr(self.server, "db", None) else None
        self._cache_stay(row or {
            "character_id": session.character_id,
            "inn_id": inn["id"],
            "checked_in_room_id": inn["front_desk_room_id"],
            "private_room_id": 0,
            "private_table_room_id": 0,
            "room_latched": 0,
        })

        await session.send_line(
            f'The desk clerk marks you down at {inn["display_name"]}.  '
            "You may now use TRAIN and FIXSTATS while staying here."
        )
        return True

    async def check_out(self, session) -> bool:
        stay = self.get_stay(session.character_id)
        if not stay:
            await session.send_line("You are not currently checked in at any inn.")
            return True

        current_inn = self.get_inn_for_room(getattr(getattr(session, "current_room", None), "id", 0))
        if not current_inn or current_inn["id"] != stay["inn_id"]:
            await session.send_line("You need to return to the inn where you are staying before you can CHECK OUT.")
            return True

        inn = self._inns.get(stay["inn_id"]) or current_inn or {"display_name": "the inn"}
        self._clear_stay(session.character_id)
        await session.send_line(f'You settle your stay and CHECK OUT of {inn["display_name"]}.')
        return True

    async def check_room(self, session) -> bool:
        room = getattr(session, "current_room", None)
        inn = self._front_desks.get(int(getattr(room, "id", 0) or 0))
        if not inn:
            await session.send_line("You need to be at an inn front desk to CHECK ROOM.")
            return True

        stay = self.get_stay(session.character_id)
        if not stay or stay.get("inn_id") != inn["id"]:
            await session.send_line("CHECK IN first, then the innkeeper can assign you a room.")
            return True

        if stay.get("private_room_id"):
            room_obj = self.server.world.get_room(int(stay["private_room_id"]))
            room_label = getattr(room_obj, "title", None) or f"room {stay['private_room_id']}"
            latch_text = "latched" if stay.get("room_latched") else "unlatched"
            await session.send_line(f"Your room is {room_label}.  It is currently {latch_text}.")
            return True

        room_id = self._first_available_room(inn)
        if room_id <= 0:
            await session.send_line("There are no private rooms available at the moment.")
            return True

        row = self.server.db.upsert_character_inn_stay(
            session.character_id,
            inn["id"],
            inn["front_desk_room_id"],
            private_room_id=room_id,
            private_table_room_id=stay.get("private_table_room_id") or None,
            room_latched=False,
        ) if getattr(self.server, "db", None) else None
        self._forget_stay(session.character_id)
        self._cache_stay(row or {
            **stay,
            "private_room_id": room_id,
            "room_latched": 0,
        })

        room_obj = self.server.world.get_room(room_id)
        room_label = getattr(room_obj, "title", None) or f"room {room_id}"
        await session.send_line(
            f"The innkeeper assigns you {room_label}.  Once inside, use LATCH or UNLATCH as needed."
        )
        return True

    async def latch(self, session, latched: bool) -> bool:
        stay = self.get_stay(session.character_id)
        room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
        if not stay or room_id <= 0 or room_id != int(stay.get("private_room_id") or 0):
            await session.send_line("You must be inside your rented inn room to do that.")
            return True

        row = self.server.db.upsert_character_inn_stay(
            session.character_id,
            stay["inn_id"],
            stay["checked_in_room_id"],
            private_room_id=stay.get("private_room_id") or None,
            private_table_room_id=stay.get("private_table_room_id") or None,
            room_latched=latched,
        ) if getattr(self.server, "db", None) else None
        self._forget_stay(session.character_id)
        self._cache_stay(row or {
            **stay,
            "room_latched": 1 if latched else 0,
        })

        await session.send_line("You latch the door." if latched else "You unlatch the door.")
        return True

    async def invite(self, session, target_name: str) -> bool:
        target_name = str(target_name or "").strip()
        if not target_name:
            await session.send_line("Invite whom?")
            return True

        stay = self.get_stay(session.character_id)
        current_room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
        if not stay:
            await session.send_line("You are not checked in anywhere right now.")
            return True

        access_kind = None
        if current_room_id == int(stay.get("private_room_id") or 0):
            access_kind = "room"
        elif current_room_id == int(stay.get("private_table_room_id") or 0):
            access_kind = "table"
        if not access_kind:
            await session.send_line("You can only INVITE someone while standing in your private room or private table area.")
            return True

        guest_row = self.server.db.get_character_by_name_basic(target_name) if getattr(self.server, "db", None) else None
        if not guest_row:
            await session.send_line(f"I do not know anyone named {target_name}.")
            return True

        guest_character_id = int(guest_row.get("id") or 0)
        if guest_character_id <= 0 or guest_character_id == int(session.character_id or 0):
            await session.send_line("That invitation would accomplish nothing.")
            return True

        if not self.server.db.grant_character_inn_access(
            session.character_id,
            guest_character_id,
            stay["inn_id"],
            current_room_id,
            access_kind,
        ):
            await session.send_line("The invitation does not seem to take hold right now.")
            return True

        self._access_by_room.setdefault(current_room_id, set()).add(guest_character_id)
        await session.send_line(f"You extend an invitation to {guest_row['name']}.")

        guest_session = self.server.sessions.find_by_name(guest_row["name"]) if hasattr(self.server, "sessions") else None
        if guest_session:
            room_label = getattr(getattr(session, "current_room", None), "title", None) or "a private area"
            await guest_session.send_line(f"{session.character_name} has invited you to {room_label}.")
        return True

    async def maybe_handle_npc_topic(self, session, npc, topic: str) -> bool:
        if not getattr(npc, "matches_service", None) or not npc.matches_service("inn"):
            return False

        topic_key = _norm(topic)
        inn = self.get_inn_for_npc(npc)
        if not inn:
            return False

        if topic_key in {"hello", "hi", "greetings", ""}:
            await session.send_line(
                npc_speech(
                    npc.display_name,
                    'says, "CHECK IN at the desk to register your stay.  Once checked in, TRAIN and FIXSTATS are available here.  Ask me about a room or a table if you need private space."',
                )
            )
            return True

        if topic_key in {"check in", "checkin", "check-in"}:
            return await self.check_in(session)

        if topic_key in {"check out", "checkout", "check-out"}:
            return await self.check_out(session)

        if "room" in topic_key:
            return await self.check_room(session)

        if "table" in topic_key or "booth" in topic_key or "alcove" in topic_key:
            return await self._assign_private_table(session, inn, speaker=npc.display_name)

        if topic_key in {"training", "train", "fixstats", "fixstat"}:
            await session.send_line(
                npc_speech(
                    npc.display_name,
                    'says, "CHECK IN first, then you can use TRAIN and FIXSTATS while you remain here."',
                )
            )
            return True

        return False

    async def _assign_private_table(self, session, inn: dict, speaker: str = "the innkeeper") -> bool:
        stay = self.get_stay(session.character_id)
        if not stay or stay.get("inn_id") != inn["id"]:
            await session.send_line(npc_speech(speaker, 'says, "CHECK IN first, then I can arrange a private table for you."'))
            return True

        if stay.get("private_table_room_id"):
            room_obj = self.server.world.get_room(int(stay["private_table_room_id"]))
            room_label = getattr(room_obj, "title", None) or f"room {stay['private_table_room_id']}"
            await session.send_line(npc_speech(speaker, f'says, "Your private table is {room_label}."'))
            return True

        table_room_id = self._first_available_table(inn)
        if table_room_id <= 0:
            await session.send_line(npc_speech(speaker, 'says, "There are no private tables free right now."'))
            return True

        row = self.server.db.upsert_character_inn_stay(
            session.character_id,
            inn["id"],
            stay["checked_in_room_id"],
            private_room_id=stay.get("private_room_id") or None,
            private_table_room_id=table_room_id,
            room_latched=bool(stay.get("room_latched")),
        ) if getattr(self.server, "db", None) else None
        self._forget_stay(session.character_id)
        self._cache_stay(row or {
            **stay,
            "private_table_room_id": table_room_id,
        })

        room_obj = self.server.world.get_room(table_room_id)
        room_label = getattr(room_obj, "title", None) or f"room {table_room_id}"
        await session.send_line(npc_speech(speaker, f'says, "I have set aside {room_label} for you."'))
        return True

    def _first_available_room(self, inn: dict) -> int:
        for room_id in inn.get("rentable_room_ids") or []:
            if int(room_id) not in self._occupied_rooms:
                return int(room_id)
        return 0

    def _first_available_table(self, inn: dict) -> int:
        for room_id in inn.get("private_table_room_ids") or []:
            if int(room_id) not in self._occupied_tables:
                return int(room_id)
        return 0

    def _clear_stay(self, character_id: int) -> None:
        stay = self.get_stay(character_id)
        if not stay:
            return
        room_id = int(stay.get("private_room_id") or 0)
        table_room_id = int(stay.get("private_table_room_id") or 0)
        if getattr(self.server, "db", None):
            if room_id > 0:
                self.server.db.revoke_character_inn_access(character_id, room_id=room_id, access_kind="room")
            if table_room_id > 0:
                self.server.db.revoke_character_inn_access(character_id, room_id=table_room_id, access_kind="table")
            self.server.db.clear_character_inn_stay(character_id)
        self._forget_stay(character_id)
        if room_id > 0:
            self._access_by_room.pop(room_id, None)
        if table_room_id > 0:
            self._access_by_room.pop(table_room_id, None)

    async def before_move(self, session, from_room, target_room_id: int, direction: str) -> bool:
        target_room_id = int(target_room_id or 0)
        character_id = int(getattr(session, "character_id", 0) or 0)

        if target_room_id in self._private_tables:
            stay = self._occupied_tables.get(target_room_id)
            if not stay:
                await session.send_line("That private table has not been assigned yet.")
                return False
            if character_id == int(stay.get("character_id") or 0):
                return True
            if character_id in self._access_by_room.get(target_room_id, set()):
                return True
            await session.send_line("That private table area is reserved.")
            return False

        if target_room_id in self._private_rooms:
            stay = self._occupied_rooms.get(target_room_id)
            if not stay:
                await session.send_line("That guest room has not been assigned yet.")
                return False
            if character_id == int(stay.get("character_id") or 0):
                return True
            if not stay.get("room_latched"):
                return True
            if character_id in self._access_by_room.get(target_room_id, set()):
                return True
            await session.send_line("The door is latched from within.")
            return False

        return True
