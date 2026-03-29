"""
traps.py
--------
Canonical trap runtime.

Loads trap definitions from scripts/data/traps.lua and resolves all
detect/disarm/open/pick trigger behavior through per-trap handlers.
"""

from __future__ import annotations

import logging
import random
import time
from typing import Dict, Iterable, List, Optional

from server.core.protocol.colors import colorize, TextPresets

log = logging.getLogger(__name__)


class TrapManager:
    """Runtime trap registry and handler dispatcher."""

    def __init__(self, server):
        self.server = server
        self._data: dict = {}
        self._defs: dict = {}
        self._spawn_cfg: dict = {}
        self._weight_tiers: list = []
        self._room_hazards: list[dict] = []
        self._scarabs: list[dict] = []
        self._rift_returns: list[dict] = []

    async def initialize(self):
        self._data = {}
        self._defs = {}
        self._spawn_cfg = {}
        self._weight_tiers = []
        try:
            lua = getattr(self.server, "lua", None)
            self._data = lua.get_traps() if lua else None
            if not isinstance(self._data, dict) or not self._data:
                raise RuntimeError("traps.lua did not return valid data")
            self._defs = dict(self._data.get("definitions") or {})
            self._spawn_cfg = dict(self._data.get("spawn") or {})
            self._weight_tiers = list(self._data.get("weight_tiers") or [])
            if not self._defs:
                raise RuntimeError("traps.lua returned no trap definitions")
            log.info("TrapManager: loaded %d trap defs from Lua", len(self._defs))
        except Exception as e:
            log.error("TrapManager initialization failed: %s", e, exc_info=True)
            self._data = {}
            self._defs = {}
            self._spawn_cfg = {}
            self._weight_tiers = []

    def get_trap_def(self, trap_type: str | None) -> Optional[dict]:
        if not trap_type:
            return None
        return self._defs.get(str(trap_type))

    def choose_random_trap(self, creature_level: int) -> Optional[str]:
        if not self._defs:
            return None
        min_level = int(self._spawn_cfg.get("min_level") or 3)
        if creature_level < min_level:
            return None
        base_chance = float(self._spawn_cfg.get("base_chance_per_level") or 0.03)
        max_chance = float(self._spawn_cfg.get("max_chance") or 0.60)
        trap_chance = min(max_chance, max(0.0, creature_level * base_chance))
        if random.random() > trap_chance:
            return None
        weights = None
        for row in self._weight_tiers:
            if not isinstance(row, dict):
                continue
            lo = int(row.get("min") or 0)
            hi = int(row.get("max") or 0)
            if lo <= creature_level <= hi:
                weights = dict(row.get("weights") or {})
                break
        if not weights and self._weight_tiers:
            weights = dict((self._weight_tiers[-1] or {}).get("weights") or {})
        if not weights:
            return None
        pool = [(trap_type, int(weight or 0)) for trap_type, weight in weights.items() if int(weight or 0) > 0]
        if not pool:
            return None
        total = sum(weight for _, weight in pool)
        roll = random.uniform(0, total)
        running = 0.0
        for trap_type, weight in pool:
            running += weight
            if roll <= running:
                return trap_type
        return pool[-1][0]

    def build_box_trap_state(self, creature_level: int) -> dict:
        trap_type = self.choose_random_trap(creature_level)
        state = {
            "trap_type": trap_type,
            "trapped": trap_type is not None,
            "trap_difficulty": (creature_level * 12 + random.randint(-5, 15)) if trap_type else 0,
            "trap_checked": False,
            "trap_detected": False,
            "trap_disarmed": False,
        }
        if trap_type == "scarab":
            state["trap_variant"] = self._choose_scarab_variant()
        else:
            state["trap_variant"] = None
        state["trap_payload"] = {}
        return state

    async def tick(self, tick_count: int):
        if tick_count % 10 != 0:
            return
        now = time.time()
        await self._tick_room_hazards(now)
        await self._tick_scarabs(now)
        await self._tick_rift_returns(now)

    async def trigger_trap(self, session, box: dict, trap: dict | None = None, *, source: str = "open"):
        """Fire a trap and dispatch to its specific handler."""
        if not session or getattr(session, "is_dead", False):
            return

        trap_type = str(box.get("trap_type") or "")
        trap = trap or self.get_trap_def(trap_type)
        if not trap:
            return

        box["trapped"] = False
        box["trap_disarmed"] = True
        box["trap_detected"] = True
        payload = dict(box.get("trap_payload") or {})
        payload["triggered_at"] = int(time.time())
        payload["trigger_source"] = source
        box["trap_payload"] = payload

        room_id = getattr(getattr(session, "current_room", None), "id", 0) or 0
        if room_id and trap.get("room_msg"):
            await self.server.world.broadcast_to_room(
                room_id,
                colorize(str(trap.get("room_msg")).replace("{name}", session.character_name), TextPresets.WARNING),
                exclude=session,
            )

        handler = getattr(self, f"_handle_{trap_type}", None) or self._handle_generic
        harmed_others = await handler(session, box, trap)
        self._persist_box_state(box)
        await self._flush_session_state(session)
        if harmed_others:
            await self._note_public_disturbance(session, room_id, trap_type, harmed_others)

    def _choose_scarab_variant(self) -> Optional[str]:
        trap = self.get_trap_def("scarab") or {}
        variants = ((trap.get("special") or {}).get("variants") or [])
        valid = [v for v in variants if isinstance(v, dict) and v.get("key")]
        if not valid:
            return None
        return random.choice(valid).get("key")

    async def _handle_generic(self, session, box: dict, trap: dict) -> list:
        damage = self._roll_damage(trap.get("base_damage"))
        await session.send_line(colorize(f"  {trap.get('fail_msg')}", TextPresets.COMBAT_MISS))
        await self._apply_damage_and_effects(session, trap, damage=damage)
        return []

    async def _handle_scarab(self, session, box: dict, trap: dict) -> list:
        variant = self._scarab_variant_for_box(box, trap)
        base_damage = self._roll_damage(trap.get("base_damage"))
        await session.send_line(colorize(f"  {variant.get('attach_line') or trap.get('fail_msg')}", TextPresets.COMBAT_MISS))
        await self._apply_damage_and_effects(session, trap, damage=base_damage)
        scarab_state = {
            "variant": variant,
            "owner_name": session.character_name,
            "victim": session,
            "room_id": getattr(getattr(session, "current_room", None), "id", 0),
            "next_tick": time.time() + int((trap.get("special") or {}).get("tick_interval") or 5),
            "expires_at": time.time() + int((trap.get("special") or {}).get("default_duration") or 30),
        }
        self._scarabs.append(scarab_state)
        room_attach = variant.get("room_attach")
        if room_attach and scarab_state["room_id"]:
            await self.server.world.broadcast_to_room(
                scarab_state["room_id"],
                colorize(str(room_attach).replace("{name}", session.character_name), TextPresets.WARNING),
                exclude=session,
            )
        box["trap_payload"] = {
            **dict(box.get("trap_payload") or {}),
            "scarab_variant": variant.get("key"),
            "scarab_returned": True,
        }
        return []

    async def _handle_gas(self, session, box: dict, trap: dict) -> list:
        damage = self._roll_damage(trap.get("base_damage"))
        await session.send_line(colorize(f"  {trap.get('fail_msg')}", TextPresets.COMBAT_MISS))
        await self._apply_damage_and_effects(session, trap, damage=damage)
        special = trap.get("special") or {}
        harmed = await self._spawn_room_hazard(
            session,
            trap_type="gas",
            room_id=getattr(getattr(session, "current_room", None), "id", 0),
            duration=int(special.get("duration") or 10),
            tick_interval=int(special.get("tick_interval") or 5),
            damage_range=special.get("same_room_damage"),
            wound_cfg=None,
            statuses=special.get("same_room_statuses") or [],
            cloud_line="The lingering gas cloud makes your lungs burn as you breathe it in!",
        )
        return harmed

    async def _handle_spores(self, session, box: dict, trap: dict) -> list:
        await session.send_line(colorize(f"  {trap.get('fail_msg')}", TextPresets.COMBAT_MISS))
        special = trap.get("special") or {}
        harmed = await self._spawn_room_hazard(
            session,
            trap_type="spores",
            room_id=getattr(getattr(session, "current_room", None), "id", 0),
            duration=int(special.get("duration") or 25),
            tick_interval=int(special.get("tick_interval") or 5),
            damage_range=special.get("same_room_damage"),
            wound_cfg=special.get("wound"),
            statuses=special.get("same_room_statuses") or [],
            cloud_line="The spore cloud invades your lungs and leaves you choking!",
        )
        return harmed

    async def _handle_sphere(self, session, box: dict, trap: dict) -> list:
        await session.send_line(colorize(f"  {trap.get('fail_msg')}", TextPresets.COMBAT_MISS))
        await self._apply_damage_and_effects(session, trap, damage=self._roll_damage(trap.get("base_damage")))
        special = trap.get("special") or {}
        return await self._apply_same_room_collateral(
            session,
            damage_range=special.get("same_room_damage"),
            statuses=special.get("same_room_statuses") or [],
            message="The elemental wave slams into you and knocks you off balance!",
        )

    async def _handle_fire_vial(self, session, box: dict, trap: dict) -> list:
        await session.send_line(colorize(f"  {trap.get('fail_msg')}", TextPresets.COMBAT_MISS))
        await self._apply_damage_and_effects(session, trap, damage=self._roll_damage(trap.get("base_damage")))
        special = trap.get("special") or {}
        return await self._apply_same_room_collateral(
            session,
            damage_range=special.get("same_room_damage"),
            statuses=[],
            message="Spraying flame catches you in the blast from the trapped container!",
        )

    async def _handle_boomer(self, session, box: dict, trap: dict) -> list:
        await session.send_line(colorize(f"  {trap.get('fail_msg')}", TextPresets.COMBAT_MISS))
        await self._apply_damage_and_effects(session, trap, damage=self._roll_damage(trap.get("base_damage")))
        special = trap.get("special") or {}
        if special.get("destroys_box"):
            box["destroyed"] = True
            box["contents"] = []
            await session.send_line(colorize("  The blast tears the container apart!", TextPresets.WARNING))
        harmed = await self._apply_same_room_collateral(
            session,
            damage_range=special.get("same_room_damage"),
            statuses=[],
            message="The explosion catches you in a wave of heat and shrapnel!",
        )
        harmed.extend(
            await self._apply_adjacent_room_collateral(
                session,
                damage_range=special.get("adjacent_room_damage"),
                message=str(special.get("adjacent_room_message") or "A heavy explosion booms nearby!"),
            )
        )
        return harmed

    async def _handle_temporal_rift(self, session, box: dict, trap: dict) -> list:
        await session.send_line(colorize(f"  {trap.get('fail_msg')}", TextPresets.COMBAT_MISS))
        await self._apply_damage_and_effects(session, trap, damage=self._roll_damage(trap.get("base_damage")))
        special = trap.get("special") or {}
        await self._transport_to_temporal_rift(
            session,
            int(special.get("destination_room_id") or 1768),
            str(special.get("same_room_message") or "The room ripples violently as the rift snaps shut."),
        )
        return []

    async def _handle_dark_crystal(self, session, box: dict, trap: dict) -> list:
        await session.send_line(colorize(f"  {trap.get('fail_msg')}", TextPresets.COMBAT_MISS))
        await self._apply_damage_and_effects(session, trap, damage=self._roll_damage(trap.get("base_damage")))
        special = trap.get("special") or {}
        pct = float(special.get("mana_burn_pct") or 0.50)
        mana_loss = int((getattr(session, "mana_current", 0) or 0) * pct)
        session.mana_current = max(0, int(getattr(session, "mana_current", 0) or 0) - mana_loss)
        if mana_loss > 0:
            await session.send_line(colorize(f"  Anti-magic tears through your reserves, draining {mana_loss} mana!", TextPresets.WARNING))
        return []

    async def _handle_glyph(self, session, box: dict, trap: dict) -> list:
        await session.send_line(colorize(f"  {trap.get('fail_msg')}", TextPresets.COMBAT_MISS))
        await self._apply_damage_and_effects(session, trap, damage=self._roll_damage(trap.get("base_damage")))
        special = trap.get("special") or {}
        return await self._apply_same_room_collateral(
            session,
            damage_range=special.get("same_room_damage"),
            statuses=special.get("same_room_statuses") or [],
            message="The magical flare rakes through you with disorienting force!",
        )

    async def _apply_damage_and_effects(self, session, trap: dict, *, damage: int):
        if damage > 0:
            await self._damage_player(session, damage, str(trap.get("damage_type") or "damage"))
        if getattr(session, "is_dead", False):
            return
        wound_cfg = trap.get("wound")
        if isinstance(wound_cfg, dict):
            await self._apply_wound_cfg(session, wound_cfg)
        for status in trap.get("statuses") or []:
            self._apply_status(session, status)

    async def _apply_wound_cfg(self, session, wound_cfg: dict):
        bridge = getattr(self.server, "wound_bridge", None)
        if not bridge:
            return
        location = self._resolve_wound_location(wound_cfg.get("location"))
        crit_rank = int(wound_cfg.get("rank") or 0)
        if not location or crit_rank <= 0:
            return
        bridge.apply_wound(session, location, crit_rank)
        bridge.sync_session_state(session)
        bridge.save_wounds_now(session)

    def _resolve_wound_location(self, location):
        if isinstance(location, list):
            options = [str(x) for x in location if x]
            return random.choice(options) if options else None
        return str(location or "")

    def _apply_status(self, session, status_row: dict):
        effect_id = str(status_row.get("id") or "").strip()
        if not effect_id:
            return
        duration = float(status_row.get("duration") or 0)
        stacks = int(status_row.get("stacks") or 1)
        magnitude = float(status_row.get("magnitude") or 1)
        if getattr(self.server, "status", None):
            self.server.status.apply(session, effect_id, duration=duration, stacks=stacks, magnitude=magnitude)

    async def _damage_player(self, session, damage: int, damage_type: str):
        if getattr(session, "is_dead", False):
            return
        damage = max(0, int(damage or 0))
        if damage <= 0:
            return
        session.health_current = max(0, int(getattr(session, "health_current", 0) or 0) - damage)
        await session.send_line(colorize(f"  You take {damage} points of {damage_type} damage!", TextPresets.WARNING))
        if session.health_current <= 0 and not getattr(session, "is_dead", False):
            await self.server.death.handle_player_death(session)

    async def _apply_same_room_collateral(self, session, *, damage_range, statuses: list, message: str) -> list:
        room = getattr(session, "current_room", None)
        if not room:
            return []
        harmed = []
        for other in list(self.server.world.get_players_in_room(room.id)):
            if other is session or getattr(other, "is_dead", False):
                continue
            damage = self._roll_damage(damage_range)
            await other.send_line(colorize(f"  {message}", TextPresets.WARNING))
            if damage > 0:
                await self._damage_player(other, damage, "impact")
            for status in statuses or []:
                self._apply_status(other, status)
            harmed.append(other)
        return harmed

    async def _apply_adjacent_room_collateral(self, session, *, damage_range, message: str) -> list:
        room = getattr(session, "current_room", None)
        if not room:
            return []
        harmed = []
        seen = set()
        for target_room_id in (room.exits or {}).values():
            if not target_room_id or target_room_id in seen:
                continue
            seen.add(target_room_id)
            occupants = list(self.server.world.get_players_in_room(int(target_room_id)))
            if not occupants:
                continue
            await self.server.world.broadcast_to_room(int(target_room_id), colorize(message, TextPresets.WARNING))
            for other in occupants:
                if getattr(other, "is_dead", False):
                    continue
                damage = self._roll_damage(damage_range)
                if damage > 0:
                    await self._damage_player(other, damage, "impact")
                harmed.append(other)
        return harmed

    async def _spawn_room_hazard(
        self,
        session,
        *,
        trap_type: str,
        room_id: int,
        duration: int,
        tick_interval: int,
        damage_range,
        wound_cfg: Optional[dict],
        statuses: list,
        cloud_line: str,
    ) -> list:
        if not room_id:
            return []
        hazard = {
            "trap_type": trap_type,
            "owner": session,
            "room_id": room_id,
            "expires_at": time.time() + max(1, int(duration)),
            "next_tick": time.time() + max(1, int(tick_interval)),
            "tick_interval": max(1, int(tick_interval)),
            "damage_range": damage_range,
            "wound_cfg": wound_cfg,
            "statuses": statuses or [],
            "message": cloud_line,
        }
        self._room_hazards.append(hazard)
        harmed = []
        for other in list(self.server.world.get_players_in_room(room_id)):
            if getattr(other, "is_dead", False):
                continue
            if other is session:
                harmed.append(other)
                continue
            harmed.append(other)
        return harmed

    async def _tick_room_hazards(self, now: float):
        kept = []
        for hazard in self._room_hazards:
            if now >= float(hazard.get("expires_at") or 0):
                continue
            if now < float(hazard.get("next_tick") or 0):
                kept.append(hazard)
                continue
            room_id = int(hazard.get("room_id") or 0)
            occupants = list(self.server.world.get_players_in_room(room_id))
            for other in occupants:
                if getattr(other, "is_dead", False):
                    continue
                await other.send_line(colorize(f"  {hazard.get('message')}", TextPresets.WARNING))
                damage = self._roll_damage(hazard.get("damage_range"))
                if damage > 0:
                    await self._damage_player(other, damage, "poison")
                if isinstance(hazard.get("wound_cfg"), dict):
                    await self._apply_wound_cfg(other, hazard.get("wound_cfg"))
                for status in hazard.get("statuses") or []:
                    self._apply_status(other, status)
            hazard["next_tick"] = now + float(hazard.get("tick_interval") or 5)
            kept.append(hazard)
        self._room_hazards = kept

    async def _tick_scarabs(self, now: float):
        kept = []
        for scarab in self._scarabs:
            victim = scarab.get("victim")
            variant = scarab.get("variant") or {}
            if not victim or not getattr(victim, "connected", True):
                continue
            if now >= float(scarab.get("expires_at") or 0):
                continue
            if getattr(victim, "is_dead", False):
                if variant.get("jump_on_death"):
                    if await self._retarget_scarab(scarab):
                        kept.append(scarab)
                    continue
                continue
            if now < float(scarab.get("next_tick") or 0):
                kept.append(scarab)
                continue
            await victim.send_line(colorize(f"  {variant.get('tick_message')}", TextPresets.WARNING))
            damage = random.randint(int(variant.get("damage_min") or 3), int(variant.get("damage_max") or 8))
            await self._damage_player(victim, damage, "puncture")
            if getattr(victim, "is_dead", False):
                if variant.get("jump_on_death"):
                    if await self._retarget_scarab(scarab):
                        kept.append(scarab)
                continue
            wound_cfg = {
                "location": variant.get("wound_location") or "right_hand",
                "rank": int(variant.get("wound_rank") or 1),
            }
            await self._apply_wound_cfg(victim, wound_cfg)
            if variant.get("applies_bleed"):
                bridge = getattr(self.server, "wound_bridge", None)
                if bridge and bridge.get_wounds(victim).get(wound_cfg["location"]):
                    bridge.get_wounds(victim)[wound_cfg["location"]]["is_bleeding"] = True
                    bridge.sync_session_state(victim)
                    bridge.save_wounds_now(victim)
            for status in variant.get("statuses") or []:
                self._apply_status(victim, status)
            scarab["next_tick"] = now + 5
            kept.append(scarab)
        self._scarabs = kept

    async def _retarget_scarab(self, scarab: dict) -> bool:
        victim = scarab.get("victim")
        room = getattr(victim, "current_room", None)
        if not room:
            return False
        candidates = [
            other for other in self.server.world.get_players_in_room(room.id)
            if other is not victim and not getattr(other, "is_dead", False)
        ]
        if not candidates:
            return False
        new_target = random.choice(candidates)
        variant = scarab.get("variant") or {}
        scarab["victim"] = new_target
        scarab["next_tick"] = time.time() + 2
        scarab["expires_at"] = time.time() + 20
        await new_target.send_line(colorize(
            f"  A {variant.get('label', 'scarab')} abandons the corpse and fastens itself to you instead!",
            TextPresets.WARNING,
        ))
        await self.server.world.broadcast_to_room(
            room.id,
            colorize(
                f"A {variant.get('label', 'scarab')} leaves {victim.character_name}'s body and leaps onto {new_target.character_name}!",
                TextPresets.WARNING,
            ),
            exclude=new_target,
        )
        return True

    async def _transport_to_temporal_rift(self, session, destination_room_id: int, room_message: str):
        current_room = getattr(session, "current_room", None)
        origin_room_id = int(getattr(current_room, "id", 0) or 0)
        if current_room:
            await self.server.world.broadcast_to_room(
                current_room.id,
                colorize(f"  {room_message}", TextPresets.WARNING),
                exclude=session,
            )
        dest_room = self.server.world.get_room(destination_room_id)
        if not dest_room:
            return
        await session.send_line(colorize("  Time and space fold in upon themselves and wrench you violently away!", TextPresets.WARNING))
        if current_room:
            self.server.world.remove_player_from_room(session, current_room.id)
        session.current_room = dest_room
        self.server.world.add_player_to_room(session, dest_room.id)
        if getattr(self.server, "db", None) and getattr(session, "character_id", None):
            try:
                self.server.db.execute_query(
                    "UPDATE characters SET current_room_id = %s WHERE id = %s",
                    (dest_room.id, session.character_id),
                )
            except Exception:
                log.error("Failed to persist temporal rift transport for %s", getattr(session, "character_name", "?"), exc_info=True)
        # A small slice of rift nastiness.
        roll = random.randint(1, 5)
        if roll == 1:
            spirit_loss = max(1, int((getattr(session, "spirit_current", 1) or 1) * 0.33))
            session.spirit_current = max(0, int(getattr(session, "spirit_current", 0) or 0) - spirit_loss)
            await session.send_line(colorize("  Dark forces tear at your soul!", TextPresets.WARNING))
        elif roll == 2:
            hp_loss = max(1, int((getattr(session, "health_current", 1) or 1) * 0.33))
            await self._damage_player(session, hp_loss, "cold")
        elif roll == 3:
            mana_loss = max(1, int((getattr(session, "mana_current", 1) or 1) * 0.50))
            session.mana_current = max(0, int(getattr(session, "mana_current", 0) or 0) - mana_loss)
            await session.send_line(colorize("  Waves of anti-magic tear at you!", TextPresets.WARNING))
        elif roll == 4:
            self._apply_status(session, {"id": "stunned", "duration": 10})
            await session.send_line(colorize("  Space collapses upon itself almost crushing you!", TextPresets.WARNING))
        else:
            self._apply_status(session, {"id": "slowed", "duration": 15})
            await session.send_line(colorize("  Things seem to slow down around you!", TextPresets.WARNING))
        session.temporal_rift_origin_room_id = origin_room_id
        session.temporal_rift_room_id = dest_room.id
        session.temporal_rift_release_at = time.time() + 45
        self._rift_returns = [
            row for row in self._rift_returns
            if row.get("session") is not session
        ]
        self._rift_returns.append({
            "session": session,
            "room_id": dest_room.id,
            "return_room_id": origin_room_id,
            "release_at": float(getattr(session, "temporal_rift_release_at", 0) or 0),
        })
        await session.send_line(colorize(
            "  The rift claws at you, but it feels unstable. If you survive, it should spit you back out before long.",
            TextPresets.SYSTEM,
        ))
        from server.core.commands.player.movement import cmd_look
        await cmd_look(session, "look", "", self.server)
        pets = getattr(self.server, "pets", None)
        if pets:
            try:
                await pets.on_room_enter(session, current_room, dest_room)
            except Exception:
                log.debug("Pet room-enter hook failed after temporal rift transport", exc_info=True)

    async def _tick_rift_returns(self, now: float):
        kept = []
        for row in self._rift_returns:
            session = row.get("session")
            if not session or not getattr(session, "connected", True):
                continue
            if getattr(session, "is_dead", False):
                kept.append(row)
                continue
            if now < float(row.get("release_at") or 0):
                kept.append(row)
                continue
            room = getattr(session, "current_room", None)
            if not room or int(getattr(room, "id", 0) or 0) != int(row.get("room_id") or 0):
                continue
            return_room_id = int(row.get("return_room_id") or 0)
            return_room = self.server.world.get_room(return_room_id)
            if not return_room:
                continue
            self.server.world.remove_player_from_room(session, room.id)
            session.current_room = return_room
            self.server.world.add_player_to_room(session, return_room.id)
            session.temporal_rift_room_id = None
            session.temporal_rift_release_at = 0
            if getattr(self.server, "db", None) and getattr(session, "character_id", None):
                try:
                    self.server.db.execute_query(
                        "UPDATE characters SET current_room_id = %s WHERE id = %s",
                        (return_room.id, session.character_id),
                    )
                except Exception:
                    log.error("Failed to persist temporal rift return for %s", getattr(session, "character_name", "?"), exc_info=True)
            await session.send_line(colorize(
                "  The temporal rift buckles and spits you back into the world of ordinary time!",
                TextPresets.EXPERIENCE,
            ))
            from server.core.commands.player.movement import cmd_look
            await cmd_look(session, "look", "", self.server)
        self._rift_returns = kept

    async def _flush_session_state(self, session):
        bridge = getattr(self.server, "wound_bridge", None)
        if bridge:
            bridge.sync_session_state(session)
            bridge.save_wounds_now(session)
        if getattr(self.server, "db", None) and getattr(session, "character_id", None):
            try:
                self.server.db.save_character_resources(
                    session.character_id,
                    getattr(session, "health_current", 0),
                    getattr(session, "mana_current", 0),
                    getattr(session, "spirit_current", 0),
                    getattr(session, "stamina_current", 0),
                    getattr(session, "silver", 0),
                )
            except Exception:
                log.error("Failed saving character resources after trap resolution", exc_info=True)

    async def _note_public_disturbance(self, offender, room_id: int, trap_type: str, harmed_players: Iterable):
        harmed = [p for p in harmed_players if getattr(p, "character_name", None)]
        if not harmed:
            return
        room = self.server.world.get_room(room_id) if room_id else None
        offense = {
            "type": "trap_public_disturbance",
            "trap_type": trap_type,
            "room_id": room_id,
            "victims": [p.character_name for p in harmed],
            "timestamp": int(time.time()),
        }
        incidents = list(getattr(offender, "justice_incidents", []) or [])
        incidents.append(offense)
        offender.justice_incidents = incidents
        if room and getattr(room, "safe", False):
            await offender.send_line(colorize(
                "  The collateral damage from that trap would be considered a serious public disturbance here.",
                TextPresets.WARNING,
            ))
        if hasattr(self.server, "npcs") and room_id:
            try:
                npcs = self.server.npcs.get_npcs_in_room(room_id)
                if any("guard" in (getattr(npc, "display_name", "") or "").lower() for npc in npcs):
                    await offender.send_line(colorize(
                        "  Nearby guards certainly noticed that trap endangering bystanders.",
                        TextPresets.WARNING,
                    ))
            except Exception:
                pass

    def _persist_box_state(self, box: dict):
        inv_id = box.get("inv_id")
        if not inv_id or not getattr(self.server, "db", None):
            return
        extra = {
            "is_locked": bool(box.get("is_locked", True)),
            "opened": bool(box.get("opened", False)),
            "lock_difficulty": int(box.get("lock_difficulty", 20) or 20),
            "trap_type": box.get("trap_type"),
            "trapped": bool(box.get("trapped", False)),
            "trap_difficulty": int(box.get("trap_difficulty", 0) or 0),
            "trap_checked": bool(box.get("trap_checked", False)),
            "trap_detected": bool(box.get("trap_detected", False)),
            "trap_disarmed": bool(box.get("trap_disarmed", False)),
            "trap_variant": box.get("trap_variant"),
            "trap_payload": dict(box.get("trap_payload") or {}),
            "pick_mod_down": int(box.get("pick_mod_down", 0) or 0),
            "contents": box.get("contents", []),
        }
        self.server.db.save_item_extra_data(inv_id, extra)

    def _scarab_variant_for_box(self, box: dict, trap: dict) -> dict:
        special = trap.get("special") or {}
        variants = [v for v in (special.get("variants") or []) if isinstance(v, dict) and v.get("key")]
        chosen = str(box.get("trap_variant") or "")
        for row in variants:
            if row.get("key") == chosen:
                return row
        if variants:
            picked = random.choice(variants)
            box["trap_variant"] = picked.get("key")
            return picked
        return {}

    @staticmethod
    def _roll_damage(damage_range) -> int:
        if not isinstance(damage_range, dict):
            return 0
        lo = int(damage_range.get("min") or 0)
        hi = int(damage_range.get("max") or lo)
        if hi < lo:
            hi = lo
        return random.randint(lo, hi)
