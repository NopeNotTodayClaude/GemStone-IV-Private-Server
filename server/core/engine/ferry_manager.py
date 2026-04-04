"""
ferry_manager.py
----------------
Timed ferry transport runtime driven by scripts/data/ferries.lua.

Supports:
  - dynamic dock boarding
  - underway room transitions
  - lore-driven waiting/travel messaging
  - ferry-specific music overrides
  - loader-driven pirate ambush encounters
"""

from __future__ import annotations

import copy
import logging
import random
import time

from server.core.entity.creature.creature_data import CREATURE_TEMPLATES, get_template
from server.core.engine.treasure import generate_box
from server.core.protocol.colors import colorize, TextPresets

log = logging.getLogger(__name__)


def _fmt_seconds(seconds: int) -> str:
    seconds = max(0, int(seconds or 0))
    if seconds >= 60:
        minutes = seconds // 60
        rem = seconds % 60
        if rem == 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        return f"{minutes} minute{'s' if minutes != 1 else ''} and {rem} second{'s' if rem != 1 else ''}"
    return f"{seconds} second{'s' if seconds != 1 else ''}"


class FerryManager:
    def __init__(self, server):
        self.server = server
        self._defs = {}
        self._state = {}

    async def initialize(self):
        self._defs = {}
        self._state = {}

        defs = getattr(self.server.lua, "get_ferries", lambda: {})() or {}
        now = time.time()
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
                "phase_started_at": now,
                "phase_budget_sec": int(ferr.get("dock_duration_sec") or 60),
                "next_lore_at": now + max(5, int(ferr.get("lore_broadcast_interval_sec") or 20)),
                "ambush_pending": False,
                "ambush_trigger_elapsed_sec": 0,
                "paused_travel_remaining_sec": 0,
                "active_creature_ids": [],
                "current_wave_index": -1,
                "wave_cleared_at": 0.0,
                "dead_party_started_at": 0.0,
                "encounter_player_count": 0,
                "encounter_target_level": 1,
                "music_zone": str((ferr.get("audio") or {}).get("default_zone") or ""),
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
            for room_id in ferr.get("underway_room_ids") or []:
                if not self.server.world.get_room(int(room_id)):
                    log.warning("Skipping ferry %s underway room %s not loaded", ferr.get("id"), room_id)
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
            await self._reconcile_passenger_rooms(ferry_id, ferr, state)
            await self._maybe_emit_lore(ferry_id, ferr, state, now)
            phase = str(state.get("phase") or "docked")
            if phase == "docked":
                if self._elapsed(state, now) >= int(ferr["dock_duration_sec"]):
                    await self._depart(ferry_id)
            elif phase == "traveling":
                await self._tick_traveling(ferry_id, ferr, state, now)
            elif phase == "pre_ambush":
                prelude = max(1, int((ferr.get("ambush") or {}).get("prelude_seconds") or 8))
                if self._elapsed(state, now) >= prelude:
                    await self._start_wave(ferry_id, 0)
            elif phase in {"ambush_wave_1", "ambush_wave_2", "ambush_wave_3", "boss_wave"}:
                await self._tick_ambush(ferry_id, ferr, state, now)
            elif phase == "loot_window":
                await self._tick_loot_window(ferry_id, ferr, state, now)

    async def _tick_traveling(self, ferry_id: str, ferr: dict, state: dict, now: float):
        if self._should_start_ambush(ferr, state) and self._elapsed(state, now) >= float(state.get("ambush_trigger_elapsed_sec") or 0):
            await self._start_prelude(ferry_id, ferr, state, now)
            return
        if self._elapsed(state, now) >= float(state.get("phase_budget_sec") or ferr.get("travel_duration_sec") or 60):
            await self._arrive(ferry_id)

    async def _tick_ambush(self, ferry_id: str, ferr: dict, state: dict, now: float):
        living_players = self._living_onboard_players(ferry_id, ferr, state)
        if not living_players:
            if not state.get("dead_party_started_at"):
                state["dead_party_started_at"] = now
            fail_after = max(5, int((ferr.get("ambush") or {}).get("dead_party_fail_seconds") or 60))
            if now - float(state.get("dead_party_started_at") or now) >= fail_after:
                await self._finish_ambush_failure(ferry_id, ferr, state)
                return
        else:
            state["dead_party_started_at"] = 0.0

        if self._living_active_creatures(state):
            return

        if not state.get("wave_cleared_at"):
            state["wave_cleared_at"] = now
            await self._broadcast_wave_clear(ferry_id, ferr, state)
            return

        delay = max(0, int((ferr.get("ambush") or {}).get("inter_wave_delay_seconds") or 0))
        if now - float(state.get("wave_cleared_at") or now) < delay:
            return

        next_wave = int(state.get("current_wave_index") or 0) + 1
        waves = list((ferr.get("ambush") or {}).get("waves") or [])
        if next_wave >= len(waves):
            await self._finish_ambush_success(ferry_id, ferr, state)
            return
        await self._start_wave(ferry_id, next_wave)

    async def _tick_loot_window(self, ferry_id: str, ferr: dict, state: dict, now: float):
        if self._elapsed(state, now) >= float(state.get("phase_budget_sec") or 30):
            state["phase"] = "traveling"
            state["phase_started_at"] = now
            state["phase_budget_sec"] = max(5, int(state.get("paused_travel_remaining_sec") or ferr.get("travel_duration_sec") or 60))
            state["paused_travel_remaining_sec"] = 0
            state["next_lore_at"] = now + max(5, int(ferr.get("lore_broadcast_interval_sec") or 20))
            await self._push_sync_for_onboard(ferry_id, ferr, state)

    async def _depart(self, ferry_id: str):
        ferr = self._defs[ferry_id]
        state = self._state[ferry_id]
        current_side = state["side"]
        target_side = self._other_side(ferr, current_side)
        now = time.time()

        side_def = ferr["sides"][current_side]
        depart_room_id = int(side_def["room_id"])
        room_msg = side_def.get("departure_room_msg")
        if room_msg:
            await self.server.world.broadcast_to_room(depart_room_id, colorize(room_msg, TextPresets.SYSTEM))

        onboard_msg = ferr.get("onboard_depart_msg")
        if onboard_msg:
            await self._broadcast_to_onboard(ferry_id, ferr, state, colorize(onboard_msg, TextPresets.SYSTEM))

        moved_sessions = await self._move_passengers_for_mode(ferr, to_underway=True)

        state["phase"] = "traveling"
        state["target_side"] = target_side
        state["phase_started_at"] = now
        state["phase_budget_sec"] = int(ferr["travel_duration_sec"])
        state["next_lore_at"] = now + max(5, int(ferr.get("lore_broadcast_interval_sec") or 20))
        state["ambush_pending"] = self._roll_ambush_pending(ferry_id, ferr, state)
        state["ambush_trigger_elapsed_sec"] = self._ambush_trigger_elapsed(ferr) if state["ambush_pending"] else 0
        state["paused_travel_remaining_sec"] = 0
        state["active_creature_ids"] = []
        state["current_wave_index"] = -1
        state["wave_cleared_at"] = 0.0
        state["dead_party_started_at"] = 0.0
        state["music_zone"] = str((ferr.get("audio") or {}).get("default_zone") or "")
        log.info(
            "Ferry %s shoved off from %s toward %s with %d passenger(s)",
            ferry_id,
            current_side,
            target_side,
            len(moved_sessions),
        )
        for session in moved_sessions:
            await self._refresh_session_view(session)
        await self._push_sync_for_onboard(ferry_id, ferr, state)

    async def _arrive(self, ferry_id: str):
        ferr = self._defs[ferry_id]
        state = self._state[ferry_id]
        arriving_side = state.get("target_side") or self._other_side(ferr, state["side"])
        now = time.time()

        moved_sessions = await self._move_passengers_for_mode(ferr, to_underway=False)

        state["phase"] = "docked"
        state["side"] = arriving_side
        state["target_side"] = None
        state["phase_started_at"] = now
        state["phase_budget_sec"] = int(ferr["dock_duration_sec"])
        state["next_lore_at"] = now + max(5, int(ferr.get("lore_broadcast_interval_sec") or 20))
        state["ambush_pending"] = False
        state["ambush_trigger_elapsed_sec"] = 0
        state["paused_travel_remaining_sec"] = 0
        state["active_creature_ids"] = []
        state["current_wave_index"] = -1
        state["wave_cleared_at"] = 0.0
        state["dead_party_started_at"] = 0.0
        state["music_zone"] = str((ferr.get("audio") or {}).get("default_zone") or "")
        log.info(
            "Ferry %s arrived on %s with %d passenger(s)",
            ferry_id,
            arriving_side,
            len(moved_sessions),
        )

        side_def = ferr["sides"][arriving_side]
        arrival_room_id = int(side_def["room_id"])
        room_msg = side_def.get("arrival_room_msg")
        if room_msg:
            await self.server.world.broadcast_to_room(arrival_room_id, colorize(room_msg, TextPresets.SYSTEM))

        onboard_msg = ferr.get("onboard_arrive_msg")
        if onboard_msg:
            await self._broadcast_to_onboard(ferry_id, ferr, state, colorize(onboard_msg, TextPresets.SYSTEM))

        for session in moved_sessions:
            await self._refresh_session_view(session)
        await self._push_sync_for_onboard(ferry_id, ferr, state)

    async def _start_prelude(self, ferry_id: str, ferr: dict, state: dict, now: float):
        elapsed_before_pause = self._elapsed(state, now)
        remaining = max(
            5,
            int((state.get("phase_budget_sec") or ferr.get("travel_duration_sec") or 60) - elapsed_before_pause),
        )
        state["phase"] = "pre_ambush"
        state["phase_started_at"] = now
        state["paused_travel_remaining_sec"] = remaining
        state["ambush_pending"] = False
        state["current_wave_index"] = -1
        state["wave_cleared_at"] = 0.0
        state["dead_party_started_at"] = 0.0
        state["encounter_player_count"] = max(1, len(self._onboard_players(ferry_id, ferr, state)))
        state["encounter_target_level"] = self._encounter_target_level(ferr, state)
        state["music_zone"] = str((ferr.get("audio") or {}).get("event_zone") or state.get("music_zone") or "")
        state["next_lore_at"] = now + max(5, int(ferr.get("lore_broadcast_interval_sec") or 20))
        await self._push_sync_for_onboard(ferry_id, ferr, state)
        message = self._pick_message((ferr.get("ambush") or {}).get("prelude_messages") or [])
        if message:
            await self._broadcast_to_onboard(ferry_id, ferr, state, colorize(message, TextPresets.WARNING))

    async def _start_wave(self, ferry_id: str, wave_index: int):
        ferr = self._defs[ferry_id]
        state = self._state[ferry_id]
        ambush = ferr.get("ambush") or {}
        waves = list(ambush.get("waves") or [])
        if wave_index < 0 or wave_index >= len(waves):
            return
        wave = dict(waves[wave_index] or {})
        phase = "boss_wave" if wave.get("boss") else f"ambush_wave_{wave_index + 1}"
        state["phase"] = phase
        state["phase_started_at"] = time.time()
        state["current_wave_index"] = wave_index
        state["wave_cleared_at"] = 0.0
        state["active_creature_ids"] = []
        state["dead_party_started_at"] = 0.0

        if wave_index == 0:
            lines = ambush.get("approach_messages") or []
        elif wave.get("boss"):
            lines = ambush.get("boss_arrival_messages") or []
        else:
            lines = ambush.get("wave_completion_messages") or []
        message = self._pick_message(lines)
        if message:
            await self._broadcast_to_onboard(ferry_id, ferr, state, colorize(message, TextPresets.WARNING))

        live_ids = []
        if wave.get("boss"):
            count = 1
        else:
            fixed_count = max(0, int(wave.get("fixed_count") or 0))
            if fixed_count > 0:
                count = fixed_count
            else:
                count = max(1, int(wave.get("per_player") or 1) * max(1, int(state.get("encounter_player_count") or 1)))
        for room_id in self._spawn_room_cycle(ferry_id, ferr, state, count):
            creature = self._spawn_variant(ferry_id, ferr, state, str(wave.get("variant_id") or ""), room_id)
            if creature:
                live_ids.append(int(creature.id))
                if wave.get("boss"):
                    self._decorate_boss_loot(ferr, state, creature, wave)

        for add in wave.get("adds") or []:
            add_variant = str((add or {}).get("variant_id") or "")
            add_count = max(0, int((add or {}).get("count") or 0))
            for room_id in self._spawn_room_cycle(ferry_id, ferr, state, add_count):
                creature = self._spawn_variant(ferry_id, ferr, state, add_variant, room_id)
                if creature:
                    live_ids.append(int(creature.id))

        state["active_creature_ids"] = live_ids

    async def _finish_ambush_success(self, ferry_id: str, ferr: dict, state: dict):
        success_line = self._pick_message((ferr.get("ambush") or {}).get("success_messages") or [])
        if success_line:
            await self._broadcast_to_onboard(ferry_id, ferr, state, colorize(success_line, TextPresets.SYSTEM))
        loot_line = self._pick_message(ferr.get("loot_window_messages") or [])
        if loot_line:
            await self._broadcast_to_onboard(ferry_id, ferr, state, colorize(loot_line, TextPresets.SYSTEM))
        state["phase"] = "loot_window"
        state["phase_started_at"] = time.time()
        state["phase_budget_sec"] = max(5, int((ferr.get("ambush") or {}).get("loot_window_seconds") or 30))
        state["music_zone"] = str((ferr.get("audio") or {}).get("default_zone") or "")
        state["active_creature_ids"] = []
        state["current_wave_index"] = -1
        state["wave_cleared_at"] = 0.0
        state["dead_party_started_at"] = 0.0
        state["next_lore_at"] = time.time() + max(5, int(ferr.get("lore_broadcast_interval_sec") or 20))
        await self._push_sync_for_onboard(ferry_id, ferr, state)

    async def _finish_ambush_failure(self, ferry_id: str, ferr: dict, state: dict):
        line = self._pick_message((ferr.get("ambush") or {}).get("failure_messages") or [])
        if line:
            await self._broadcast_to_onboard(ferry_id, ferr, state, colorize(line, TextPresets.WARNING))
        self._clear_active_creatures(state)
        state["phase"] = "traveling"
        state["phase_started_at"] = time.time()
        state["phase_budget_sec"] = max(5, int(state.get("paused_travel_remaining_sec") or ferr.get("travel_duration_sec") or 60))
        state["paused_travel_remaining_sec"] = 0
        state["music_zone"] = str((ferr.get("audio") or {}).get("default_zone") or "")
        state["current_wave_index"] = -1
        state["wave_cleared_at"] = 0.0
        state["dead_party_started_at"] = 0.0
        state["next_lore_at"] = time.time() + max(5, int(ferr.get("lore_broadcast_interval_sec") or 20))
        await self._push_sync_for_onboard(ferry_id, ferr, state)

    async def _broadcast_wave_clear(self, ferry_id: str, ferr: dict, state: dict):
        ambush = ferr.get("ambush") or {}
        wave_index = int(state.get("current_wave_index") or 0)
        waves = list(ambush.get("waves") or [])
        if wave_index >= len(waves) - 1:
            return
        message = self._pick_message(ambush.get("wave_completion_messages") or [])
        if message:
            await self._broadcast_to_onboard(ferry_id, ferr, state, colorize(message, TextPresets.WARNING))

    async def _maybe_emit_lore(self, ferry_id: str, ferr: dict, state: dict, now: float):
        if now < float(state.get("next_lore_at") or 0.0):
            return
        phase = str(state.get("phase") or "docked")
        if phase == "docked":
            current_side = state.get("side")
            side_def = ferr["sides"].get(current_side) or {}
            room_id = int(side_def.get("room_id") or 0)
            msg = self._pick_message(ferr.get("waiting_room_lines") or [])
            if room_id > 0 and msg:
                await self.server.world.broadcast_to_room(room_id, colorize(msg, TextPresets.SYSTEM))
        elif phase == "traveling":
            msg = self._pick_message(ferr.get("travel_messages") or [])
            if msg:
                await self._broadcast_to_onboard(ferry_id, ferr, state, colorize(msg, TextPresets.SYSTEM))
        elif phase == "loot_window":
            msg = self._pick_message(ferr.get("loot_window_messages") or [])
            if msg:
                await self._broadcast_to_onboard(ferry_id, ferr, state, colorize(msg, TextPresets.SYSTEM))
        state["next_lore_at"] = now + max(5, int(ferr.get("lore_broadcast_interval_sec") or 20))

    def _roll_ambush_pending(self, ferry_id: str, ferr: dict, state: dict) -> bool:
        ambush = ferr.get("ambush") or {}
        if not ambush.get("enabled"):
            return False
        if not self._onboard_players(ferry_id, ferr, state):
            return False
        chance = max(0, min(100, int(ambush.get("chance_pct") or 0)))
        return random.randint(1, 100) <= chance

    def _should_start_ambush(self, ferr: dict, state: dict) -> bool:
        ambush = ferr.get("ambush") or {}
        return bool(
            ambush.get("enabled")
            and state.get("ambush_pending")
            and not state.get("active_creature_ids")
            and self._onboard_players_from_rooms(self._current_onboard_room_ids(ferr, state))
        )

    def _ambush_trigger_elapsed(self, ferr: dict) -> int:
        ambush = ferr.get("ambush") or {}
        travel = max(5, int(ferr.get("travel_duration_sec") or 60))
        min_pct = max(1, min(95, int(ambush.get("trigger_progress_min_pct") or 50)))
        max_pct = max(min_pct, min(95, int(ambush.get("trigger_progress_max_pct") or min_pct)))
        return max(1, int(travel * random.randint(min_pct, max_pct) / 100))

    def _encounter_target_level(self, ferr: dict, state: dict) -> int:
        ambush = ferr.get("ambush") or {}
        players = self._onboard_players_from_rooms(self._current_onboard_room_ids(ferr, state))
        levels = [max(1, int(getattr(session, "level", 1) or 1)) for session in players]
        average = round(sum(levels) / len(levels)) if levels else 1
        scale_pct = max(25, min(150, int(ambush.get("average_level_scale_pct") or 100)))
        level_bias = int(ambush.get("average_level_bias") or 0)
        average = max(1, int(round((average * scale_pct) / 100.0)) + level_bias)
        floor = max(1, int(ambush.get("average_level_floor") or 1))
        ceiling = max(floor, int(ambush.get("average_level_ceiling") or floor))
        return max(floor, min(ceiling, int(average)))

    def _scaled_template(self, template_id: str, base: dict, variant: dict, target_level: int) -> dict:
        base_level = max(1, int(base.get("level", 1) or 1))
        level_scale = max(0.50, float(target_level) / float(base_level))
        hp_mult = max(0.10, float(variant.get("hp_mult") or 1.0))
        hp_bonus = int(variant.get("hp_bonus") or 0)
        as_mult = max(0.10, float(variant.get("as_mult") or 1.0))
        as_bonus = int(variant.get("as_bonus") or 0)
        ds_mult = max(0.10, float(variant.get("ds_mult") or 1.0))
        ds_bonus = int(variant.get("ds_bonus") or 0)
        td_mult = max(0.10, float(variant.get("td_mult") or 1.0))
        td_bonus = int(variant.get("td_bonus") or 0)

        tmpl = copy.deepcopy(base)
        tmpl["template_id"] = template_id
        tmpl["name"] = str(variant.get("name") or base.get("name") or "creature")
        tmpl["article"] = str(variant.get("article") or base.get("article") or "a")
        tmpl["description"] = str(variant.get("description") or base.get("description") or "")
        tmpl["level"] = max(1, int(target_level))
        base_hp = int(base.get("hp", base.get("health_max", 30)) or 30)
        tmpl["hp"] = max(10, int((base_hp * level_scale * hp_mult) + hp_bonus))
        tmpl["hp_variance"] = max(1, int(base.get("hp_variance", 4) or 4))
        base_as = int(base.get("as_melee", 25) or 25)
        tmpl["as_melee"] = max(5, int((base_as * level_scale * as_mult) + as_bonus))
        base_ds = int(base.get("ds_melee", 10) or 10)
        tmpl["ds_melee"] = max(0, int((base_ds * level_scale * ds_mult) + ds_bonus))
        tmpl["ds_ranged"] = max(0, int((int(base.get("ds_ranged", base_ds) or base_ds) * level_scale * ds_mult) + ds_bonus))
        tmpl["ds_bolt"] = max(0, int((int(base.get("ds_bolt", base_ds) or base_ds) * level_scale * ds_mult) + ds_bonus))
        base_td = int(base.get("td", base_level * 3) or (base_level * 3))
        tmpl["td"] = max(5, int((base_td * level_scale * td_mult) + td_bonus))
        tmpl["td_spiritual"] = max(5, int((int(base.get("td_spiritual", base_td) or base_td) * level_scale * td_mult) + td_bonus))
        tmpl["td_elemental"] = max(5, int((int(base.get("td_elemental", base_td) or base_td) * level_scale * td_mult) + td_bonus))
        tmpl["treasure"] = dict(variant.get("treasure") or {"coins": False, "gems": False, "magic": False, "boxes": False})
        attacks = []
        for attack in list(base.get("attacks") or []):
            row = dict(attack or {})
            base_attack_as = int(row.get("as", base_as) or base_as)
            row["as"] = max(5, int((base_attack_as * level_scale * as_mult) + as_bonus))
            attacks.append(row)
        if attacks:
            tmpl["attacks"] = attacks
        return tmpl

    def _spawn_variant(self, ferry_id: str, ferr: dict, state: dict, variant_id: str, room_id: int):
        if room_id <= 0:
            return None
        variant = dict(((ferr.get("ambush") or {}).get("variants") or {}).get(variant_id) or {})
        base_template_id = str(variant.get("base_template_id") or "").strip()
        base = copy.deepcopy(get_template(base_template_id) or {})
        if not base:
            log.warning("FerryManager: missing base template '%s' for ferry variant '%s'", base_template_id, variant_id)
            return None
        target_level = max(1, int(state.get("encounter_target_level") or 1) + int(variant.get("level_offset") or 0))
        template_id = f"ferry_{ferry_id}_{variant_id}_{target_level}_{int(time.time())}"
        CREATURE_TEMPLATES[template_id] = self._scaled_template(template_id, base, variant, target_level)
        spawn_context = {
            "special_spawn": True,
            "allow_safe_room": True,
            "ignore_bubble_cull": True,
            "ferry_id": ferry_id,
            "ferry_event_hostile": True,
            "ferry_variant": variant_id,
            "ferry_phase": str(state.get("phase") or ""),
        }
        creature = self.server.creatures.spawn_creature(
            template_id,
            int(room_id),
            allow_safe=True,
            spawn_context=spawn_context,
        )
        if creature:
            creature.aggressive = True
        return creature

    def _decorate_boss_loot(self, ferr: dict, state: dict, creature, wave: dict):
        db = getattr(self.server, "db", None)
        if not db:
            return
        ambush = ferr.get("ambush") or {}
        extra_min = max(0, int(ambush.get("captain_extra_boxes_min") or 0))
        extra_max = max(extra_min, int(ambush.get("captain_extra_boxes_max") or extra_min))
        extra_boxes = random.randint(extra_min, extra_max) if extra_max > 0 else 0
        for _ in range(extra_boxes):
            try:
                box = generate_box(db, max(1, int(state.get("encounter_target_level") or 1)), server=self.server)
            except Exception:
                box = None
            if box:
                creature.stolen_items.append(dict(box))

        hat_drop = dict(wave.get("hat_drop") or {})
        if not hat_drop.get("enabled"):
            return
        chance = max(0, min(100, int(hat_drop.get("chance_pct") or ambush.get("hat_drop_chance_pct") or 0)))
        if random.randint(1, 100) > chance:
            return
        item_name = str(hat_drop.get("item_name") or "").strip()
        if not item_name:
            return
        rows = db.execute_query("SELECT id, short_name, noun, article, description FROM items WHERE name = %s LIMIT 1", (item_name,))
        if not rows:
            return
        row = rows[0]
        short_name = row[1] or item_name
        creature.stolen_items.append(
            {
                "item_id": int(row[0]),
                "name": item_name,
                "short_name": short_name,
                "noun": row[2] or "hat",
                "article": row[3] or "a",
                "item_type": "armor",
                "worn_location": "head",
                "description": row[4] or "A weathered black pirate hat.",
                **{str(k): v for k, v in ((hat_drop.get("extra_data") or {}).items())},
            }
        )

    def _clear_active_creatures(self, state: dict):
        creatures = getattr(self.server, "creatures", None)
        if not creatures:
            return
        for creature_id in list(state.get("active_creature_ids") or []):
            creature = creatures.get_creature(int(creature_id or 0))
            if creature:
                creatures.remove_creature(creature)
        state["active_creature_ids"] = []

    def _living_active_creatures(self, state: dict) -> list[int]:
        creatures = getattr(self.server, "creatures", None)
        if not creatures:
            state["active_creature_ids"] = []
            return []
        live = []
        for creature_id in list(state.get("active_creature_ids") or []):
            creature = creatures.get_creature(int(creature_id or 0))
            if creature and getattr(creature, "alive", False):
                live.append(int(creature.id))
        state["active_creature_ids"] = live
        return live

    def _spawn_room_cycle(self, ferry_id: str, ferr: dict, state: dict, count: int) -> list[int]:
        if count <= 0:
            return []
        current_rooms = self._current_onboard_room_ids(ferr, state)
        occupancy = []
        for room_id in current_rooms:
            living_count = len(
                [
                    session for session in self.server.world.get_players_in_room(room_id)
                    if not getattr(session, "is_dead", False)
                ]
            )
            if living_count > 0:
                occupancy.extend([room_id] * living_count)
        if not occupancy:
            occupancy = [int(current_rooms[0])] if current_rooms else [int(ferr.get("ferry_room_id") or 0)]
        return [occupancy[idx % len(occupancy)] for idx in range(count)]

    async def _broadcast_to_onboard(self, ferry_id: str, ferr: dict, state: dict, message: str):
        sent = set()
        for room_id in self._current_onboard_room_ids(ferr, state):
            room_id = int(room_id or 0)
            if room_id <= 0 or room_id in sent:
                continue
            sent.add(room_id)
            await self.server.world.broadcast_to_room(room_id, message)

    async def _move_passengers_for_mode(self, ferr: dict, *, to_underway: bool):
        transitions = dict((ferr.get("room_transitions") or {}).get("underway" if to_underway else "docked") or {})
        if not transitions:
            return []
        moved_sessions = []
        for src_room_id, dest_room_id in transitions.items():
            src_room_id = int(src_room_id or 0)
            dest_room_id = int(dest_room_id or 0)
            for session in list(self.server.world.get_players_in_room(src_room_id)):
                await self._transport_session(session, dest_room_id)
                moved_sessions.append(session)
        return moved_sessions

    async def _reconcile_passenger_rooms(self, ferry_id: str, ferr: dict, state: dict):
        phase = str(state.get("phase") or "docked")
        to_underway = phase in {
            "traveling",
            "pre_ambush",
            "ambush_wave_1",
            "ambush_wave_2",
            "ambush_wave_3",
            "boss_wave",
            "loot_window",
        }
        transitions = dict((ferr.get("room_transitions") or {}).get("underway" if to_underway else "docked") or {})
        if not transitions:
            return

        corrected = []
        for src_room_id, dest_room_id in transitions.items():
            src_room_id = int(src_room_id or 0)
            dest_room_id = int(dest_room_id or 0)
            if src_room_id <= 0 or dest_room_id <= 0:
                continue
            for session in list(self.server.world.get_players_in_room(src_room_id)):
                await self._transport_session(session, dest_room_id)
                corrected.append((session, src_room_id, dest_room_id))

        if corrected:
            log.info(
                "Ferry %s reconciled %d passenger room mismatch(es) during %s",
                ferry_id,
                len(corrected),
                phase,
            )
            for session, _src_room_id, _dest_room_id in corrected:
                await self._refresh_session_view(session)

    async def _transport_session(self, session, room_id: int):
        target_room = self.server.world.get_room(int(room_id or 0))
        current_room = getattr(session, "current_room", None)
        if not target_room or not current_room or current_room.id == target_room.id:
            return
        self.server.world.remove_player_from_room(session, current_room.id)
        self.server.world.add_player_to_room(session, target_room.id)
        session.previous_room = current_room
        session.current_room = target_room
        db = getattr(self.server, "db", None)
        if db and getattr(session, "character_id", None):
            try:
                db.save_character_room(session.character_id, target_room.id)
            except Exception:
                log.exception("Failed saving ferry room change for %s", getattr(session, "character_name", "?"))
        pets = getattr(self.server, "pets", None)
        if pets:
            try:
                await pets.on_room_enter(session, current_room, target_room)
            except Exception:
                log.debug("Pet ferry transport hook failed", exc_info=True)

    async def _refresh_session_view(self, session):
        try:
            from server.core.commands.player.movement import cmd_look
            await cmd_look(session, "look", "", self.server)
        except Exception:
            log.debug("Failed refreshing ferry passenger room look", exc_info=True)
        broadcaster = getattr(self.server, "sync_broadcaster", None)
        if broadcaster:
            try:
                await broadcaster.broadcast_session(session)
            except Exception:
                log.debug("Failed refreshing ferry passenger sync", exc_info=True)

    async def _push_sync_for_onboard(self, ferry_id: str, ferr: dict, state: dict):
        broadcaster = getattr(self.server, "sync_broadcaster", None)
        if not broadcaster:
            return
        for session in self._onboard_players(ferry_id, ferr, state):
            try:
                await broadcaster.broadcast_session(session)
            except Exception:
                log.debug("Failed ferry audio sync refresh for %s", getattr(session, "character_name", "?"), exc_info=True)

    def _onboard_players(self, ferry_id: str, ferr: dict, state: dict):
        return self._onboard_players_from_rooms(self._current_onboard_room_ids(ferr, state))

    def _living_onboard_players(self, ferry_id: str, ferr: dict, state: dict):
        return [
            session for session in self._onboard_players(ferry_id, ferr, state)
            if not getattr(session, "is_dead", False)
        ]

    def _onboard_players_from_rooms(self, room_ids: list[int]):
        players = []
        seen = set()
        for room_id in room_ids:
            for session in self.server.world.get_players_in_room(int(room_id or 0)):
                sid = int(getattr(session, "id", 0) or 0)
                if sid in seen:
                    continue
                seen.add(sid)
                players.append(session)
        return players

    def _current_onboard_room_ids(self, ferr: dict, state: dict) -> list[int]:
        phase = str(state.get("phase") or "docked")
        if phase in {"traveling", "pre_ambush", "ambush_wave_1", "ambush_wave_2", "ambush_wave_3", "boss_wave", "loot_window"}:
            return [int(rid) for rid in (ferr.get("underway_room_ids") or ferr.get("onboard_room_ids") or []) if int(rid or 0) > 0]
        return [int(rid) for rid in (ferr.get("onboard_room_ids") or []) if int(rid or 0) > 0]

    def _other_side(self, ferr: dict, current_side: str) -> str:
        for side_name in ferr["sides"].keys():
            if side_name != current_side:
                return side_name
        return current_side

    def _elapsed(self, state: dict, now: float | None = None) -> float:
        if now is None:
            now = time.time()
        return float(now) - float(state.get("phase_started_at") or now)

    def _pick_message(self, lines: list[str]) -> str:
        choices = [str(line or "").strip() for line in (lines or []) if str(line or "").strip()]
        return random.choice(choices) if choices else ""

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
        now = time.time()
        for ferry_id, ferr in self._defs.items():
            state = self._state.get(ferry_id) or {}
            phase = str(state.get("phase") or "docked")
            current_side = state.get("side")
            side_def = ferr["sides"].get(current_side) or {}
            dock_room_id = int(side_def.get("room_id") or 0)
            onboard_room_ids = set(self._current_onboard_room_ids(ferr, state))

            if phase == "docked" and room_id == dock_room_id:
                entity_line = side_def.get("entity_line")
                ferryman_line = side_def.get("ferryman_line")
                if entity_line:
                    lines.append(entity_line)
                if ferryman_line:
                    lines.append(ferryman_line)
                remaining = max(0, int((state.get("phase_budget_sec") or ferr.get("dock_duration_sec") or 60) - self._elapsed(state, now)))
                for row in ferr.get("waiting_room_countdown_lines") or []:
                    if remaining <= int(row.get("seconds") or 0):
                        lines.append(colorize(str(row.get("line") or "").replace("%time_remaining%", _fmt_seconds(remaining)), TextPresets.SYSTEM))
                        break
                for text in ferr.get("waiting_room_lines") or []:
                    lines.append(colorize(text, TextPresets.SYSTEM))
                continue

            if room_id in onboard_room_ids:
                if phase == "traveling":
                    remaining = max(0, int((state.get("phase_budget_sec") or ferr.get("travel_duration_sec") or 60) - self._elapsed(state, now)))
                    lines.append(colorize(f"The far pier lies roughly {_fmt_seconds(remaining)} away at the ferry's current pace.", TextPresets.SYSTEM))
                elif phase == "pre_ambush":
                    lines.append(colorize("The ferry has gone tense and slow on the water, as though the crew are waiting for something to break from the dark.", TextPresets.WARNING))
                elif phase in {"ambush_wave_1", "ambush_wave_2", "ambush_wave_3", "boss_wave"}:
                    lines.append(colorize("The ferry's progress is frozen while dead raiders crowd the rails and the crew fight to keep the boat from turning broadside.", TextPresets.WARNING))
                elif phase == "loot_window":
                    lines.append(colorize("The ferry is holding position long enough for the survivors to loot the dead and get their breathing back.", TextPresets.SYSTEM))
                for text in (dict(ferr.get("onboard_status_lines") or {}).get(phase) or []):
                    lines.append(colorize(text, TextPresets.SYSTEM))
        return lines

    def describe_target(self, room_id: int, target: str) -> list[str] | None:
        room_id = int(room_id or 0)
        target_l = str(target or "").lower().strip()
        for ferry_id, ferr in self._defs.items():
            state = self._state.get(ferry_id) or {}
            side_def = ferr["sides"].get(state.get("side")) or {}
            ferry_room_id = int(ferr["ferry_room_id"])
            dock_room_id = int(side_def.get("room_id") or 0)
            relevant_rooms = {dock_room_id, ferry_room_id}
            relevant_rooms.update(int(rid) for rid in (ferr.get("onboard_room_ids") or []))
            relevant_rooms.update(int(rid) for rid in (ferr.get("underway_room_ids") or []))
            if room_id not in relevant_rooms:
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

    def get_audio_zone_override(self, room_id: int) -> str | None:
        room_id = int(room_id or 0)
        for ferry_id, ferr in self._defs.items():
            state = self._state.get(ferry_id) or {}
            if room_id not in set(self._current_onboard_room_ids(ferr, state)):
                continue
            override = str(state.get("music_zone") or (ferr.get("audio") or {}).get("default_zone") or "").strip()
            if override:
                return override
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
            return True
        return True
