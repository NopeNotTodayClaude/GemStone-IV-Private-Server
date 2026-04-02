"""
ferry_manager.py
----------------
Timed ferry transport runtime driven by scripts/data/ferries.lua.

The manager exposes:
  - dynamic room exits while a ferry is docked
  - dock/onboard room look lines
  - simple ferry/ferryman LOOK targets
  - boarding toll collection
  - timed depart/arrive state changes on the main game loop
"""

import logging
import time

from server.core.protocol.colors import colorize, TextPresets

log = logging.getLogger(__name__)


class FerryManager:
    def __init__(self, server):
        self.server = server
        self._defs = {}
        self._state = {}

    async def initialize(self):
        self._defs = {}
        self._state = {}

        defs = getattr(self.server.lua, "get_ferries", lambda: {})() or {}
        for ferry_id, ferr in defs.items():
            if not self._validate_definition(ferr):
                continue
            start_side = ferr["start_side"]
            if start_side not in ferr["sides"]:
                start_side = next(iter(ferr["sides"].keys()))

            self._defs[ferry_id] = ferr
            self._state[ferry_id] = {
                "phase": "docked",
                "side": start_side,
                "target_side": None,
                "phase_started_at": time.time(),
            }

        log.info("FerryManager ready (%d routes)", len(self._defs))

    def _validate_definition(self, ferr: dict) -> bool:
        try:
            ferry_room = int(ferr["ferry_room_id"])
            if not self.server.world.get_room(ferry_room):
                log.warning("Skipping ferry %s: ferry room %s not loaded", ferr.get("id"), ferry_room)
                return False
            for side_name, side in ferr["sides"].items():
                room_id = int(side["room_id"])
                if not self.server.world.get_room(room_id):
                    log.warning("Skipping ferry %s side %s: room %s not loaded", ferr.get("id"), side_name, room_id)
                    return False
            return True
        except Exception as e:
            log.warning("Skipping invalid ferry definition %s: %s", ferr, e)
            return False

    async def tick(self, tick_count: int):
        if tick_count % 10 != 0:
            return

        now = time.time()
        for ferry_id, ferr in self._defs.items():
            state = self._state.get(ferry_id)
            if not state:
                continue
            elapsed = now - float(state.get("phase_started_at") or now)
            if state["phase"] == "docked":
                if elapsed >= int(ferr["dock_duration_sec"]):
                    await self._depart(ferry_id)
            elif state["phase"] == "traveling":
                if elapsed >= int(ferr["travel_duration_sec"]):
                    await self._arrive(ferry_id)

    async def _depart(self, ferry_id: str):
        ferr = self._defs[ferry_id]
        state = self._state[ferry_id]
        current_side = state["side"]
        target_side = self._other_side(ferr, current_side)
        state["phase"] = "traveling"
        state["target_side"] = target_side
        state["phase_started_at"] = time.time()

        side_def = ferr["sides"][current_side]
        depart_room_id = int(side_def["room_id"])
        room_msg = side_def.get("departure_room_msg")
        if room_msg:
            await self.server.world.broadcast_to_room(depart_room_id, colorize(room_msg, TextPresets.SYSTEM))

        onboard_msg = ferr.get("onboard_depart_msg")
        if onboard_msg:
            await self._broadcast_to_onboard(ferr, colorize(onboard_msg, TextPresets.SYSTEM))

    async def _arrive(self, ferry_id: str):
        ferr = self._defs[ferry_id]
        state = self._state[ferry_id]
        arriving_side = state.get("target_side") or self._other_side(ferr, state["side"])
        state["phase"] = "docked"
        state["side"] = arriving_side
        state["target_side"] = None
        state["phase_started_at"] = time.time()

        side_def = ferr["sides"][arriving_side]
        arrival_room_id = int(side_def["room_id"])
        room_msg = side_def.get("arrival_room_msg")
        if room_msg:
            await self.server.world.broadcast_to_room(arrival_room_id, colorize(room_msg, TextPresets.SYSTEM))

        onboard_msg = ferr.get("onboard_arrive_msg")
        if onboard_msg:
            await self._broadcast_to_onboard(ferr, colorize(onboard_msg, TextPresets.SYSTEM))

    async def _broadcast_to_onboard(self, ferr: dict, message: str):
        sent = set()
        for room_id in ferr.get("onboard_room_ids") or []:
            room_id = int(room_id)
            if room_id in sent:
                continue
            sent.add(room_id)
            await self.server.world.broadcast_to_room(room_id, message)

    def _other_side(self, ferr: dict, current_side: str) -> str:
        for side_name in ferr["sides"].keys():
            if side_name != current_side:
                return side_name
        return current_side

    def get_dynamic_room_exits(self, session, room) -> dict:
        exits = {}
        room_id = int(getattr(room, "id", 0) or 0)
        for ferry_id, ferr in self._defs.items():
            state = self._state.get(ferry_id) or {}
            if state.get("phase") != "docked":
                continue
            current_side = state.get("side")
            side_def = ferr["sides"].get(current_side) or {}
            dock_room_id = int(side_def.get("room_id") or 0)
            ferry_room_id = int(ferr["ferry_room_id"])
            exit_key = str(ferr.get("boarding_exit") or "go_plank")

            if room_id == dock_room_id:
                exits[exit_key] = ferry_room_id
            elif room_id == ferry_room_id:
                exits[exit_key] = dock_room_id
        return exits

    def get_room_lines(self, room_id: int, session=None) -> list[str]:
        lines = []
        room_id = int(room_id or 0)
        for ferry_id, ferr in self._defs.items():
            state = self._state.get(ferry_id) or {}
            if state.get("phase") != "docked":
                continue
            side_def = ferr["sides"].get(state.get("side")) or {}
            if room_id != int(side_def.get("room_id") or 0):
                continue
            entity_line = side_def.get("entity_line")
            ferryman_line = side_def.get("ferryman_line")
            if entity_line:
                lines.append(entity_line)
            if ferryman_line:
                lines.append(ferryman_line)
        return lines

    def describe_target(self, room_id: int, target: str) -> list[str] | None:
        room_id = int(room_id or 0)
        target_l = str(target or "").lower().strip()
        for ferry_id, ferr in self._defs.items():
            state = self._state.get(ferry_id) or {}
            side_def = ferr["sides"].get(state.get("side")) or {}
            ferry_room_id = int(ferr["ferry_room_id"])
            dock_room_id = int(side_def.get("room_id") or 0)
            if room_id not in {dock_room_id, ferry_room_id}:
                continue

            if any(token in target_l for token in ("ferry", "ferryboat", "boat")):
                desc = ferr.get("ferry_look")
                if desc:
                    return [desc]
            if "ferryman" in target_l:
                desc = ferr.get("ferryman_look")
                if desc:
                    return [desc]
        return None

    async def before_move(self, session, from_room, target_room_id: int, exit_key: str) -> bool:
        if not from_room:
            return True
        room_id = int(getattr(from_room, "id", 0) or 0)
        target_room_id = int(target_room_id or 0)
        normalized = str(exit_key or "").strip().lower().replace("-", "_").replace(" ", "_")

        for ferry_id, ferr in self._defs.items():
            state = self._state.get(ferry_id) or {}
            if state.get("phase") != "docked":
                continue
            current_side = state.get("side")
            side_def = ferr["sides"].get(current_side) or {}
            dock_room_id = int(side_def.get("room_id") or 0)
            ferry_room_id = int(ferr["ferry_room_id"])
            boarding_exit = str(ferr.get("boarding_exit") or "go_plank").lower()

            if room_id != dock_room_id or target_room_id != ferry_room_id:
                continue
            if normalized != boarding_exit:
                continue

            fare = int(side_def.get("fare") or 0)
            if fare > 0:
                current_silver = int(getattr(session, "silver", 0) or 0)
                if current_silver < fare:
                    deny = side_def.get("deny_msg") or "You do not have enough silver for the crossing."
                    await session.send_line(colorize(deny, TextPresets.WARNING))
                    return False
                session.silver = current_silver - fare
                db = getattr(self.server, "db", None)
                if db and getattr(session, "character_id", None):
                    try:
                        db.save_character_resources(
                            session.character_id,
                            int(getattr(session, "health_current", 0) or 0),
                            int(getattr(session, "mana_current", 0) or 0),
                            int(getattr(session, "spirit_current", 0) or 0),
                            int(getattr(session, "stamina_current", 0) or 0),
                            int(session.silver or 0),
                        )
                    except Exception:
                        pass
                board_msg = side_def.get("board_msg")
                if board_msg:
                    await session.send_line(colorize(board_msg, TextPresets.SYSTEM))
            else:
                board_msg = side_def.get("board_msg")
                if board_msg:
                    await session.send_line(colorize(board_msg, TextPresets.SYSTEM))
            return True
        return True
