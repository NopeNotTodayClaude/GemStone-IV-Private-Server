"""
npc_manager.py
--------------
NPCManager — Spawns, tracks, and ticks all NPCs in the game world.

Load order at startup:
    1. Lua files  — scripts/npcs/*.lua  (authoritative for new NPCs)
    2. SQL table  — npcs registry + npc_state (room overrides, alive state)
    3. Hardcoded  — npc_data.NPC_TEMPLATES (legacy, backward-compat)
    Lua wins over hardcoded on template_id collision.

Per-tick responsibilities (every game tick = 0.1s):
    every  5s  — ambient emotes (can_emote)
    every  5s  — chat lines     (can_chat)
    every  1s  — patrol move check (can_wander, per-NPC move_interval gate)
    every  1s  — combat AI       (can_combat + in_combat)
    every 10s  — loot scan       (can_loot)
    every 10s  — bot AI step     (is_bot)
    every 60s  — guard shifts
    every 60s  — respawn check

Capabilities wired up in this file:
    [x] can_emote     — ambient emotes
    [x] can_chat      — random room speech
    [x] can_wander    — patrol movement with directional messages
    [x] can_combat    — attacks players/creatures, uses CombatEngine
    [x] can_loot      — collects silver from dead creatures in room
    [x] is_bot        — stub tick (flees when injured, returns to rest room)
    [ ] is_guild      — hooked, full implementation via quest engine
    [ ] is_quest      — hooked, full implementation via quest engine
    [ ] is_house      — stub
    [ ] is_invasion   — stub (invasion manager calls on_invasion hook)
"""

import random
import time
import logging
import os
from typing import Dict, List, Optional

from server.core.entity.npc.npc import NPC
from server.core.entity.npc.npc_data import NPC_TEMPLATES
from server.core.entity.npc.npc_lua_loader import load_all_npc_luas
from server.core.protocol.colors import npc_emote, npc_speech, npc_name, colorize, TextPresets

log = logging.getLogger(__name__)

SHIFT_INTERVAL = 28800  # 8 hours in seconds

_DEPARTURE_BY_DIR = {
    "north": "heads north.", "south": "heads south.",
    "east":  "heads east.",  "west":  "heads west.",
    "up":    "heads upward.", "down": "heads downward.",
}
_ARRIVAL_BY_DIR = {
    "north": "arrives from the south.", "south": "arrives from the north.",
    "east":  "arrives from the west.",  "west":  "arrives from the east.",
    "up":    "arrives from below.",     "down":  "arrives from above.",
}

_SHIFT_DEPARTURE_LINES = {
    "amaranth": [
        "{name} hands over the post with a crisp salute.",
        "{name} gives a final scan of the road and steps aside.",
        "{name} murmurs a brief handoff report and departs.",
    ],
    "vermilion": [
        "{name} passes a quiet word to the incoming guard, then steps away.",
        "{name} gives a last look beyond the gate before departing.",
        "{name} straightens, salutes, and leaves the post.",
    ],
    "annatto": [
        "{name} lets out a long breath.  'Finally.'  The handoff is made.",
        "{name} brightens considerably at the sight of relief and hands over the post.",
        "{name} steps aside with visible relief.",
    ],
    "victory": [
        "{name} stands in place a moment after the relief arrives, then silently departs.",
        "{name} touches the gate wall once, then walks away.",
        "{name} passes the watch without ceremony.",
    ],
}

_SHIFT_ARRIVAL_LINES = {
    "amaranth": [
        "{name} takes the post with a nod.",
        "{name} arrives, shoulders straight, and assumes the watch.",
        "{name} settles into position at the Amaranth Gate.",
    ],
    "vermilion": [
        "{name} takes position at the Vermilion Gate without comment.",
        "{name} arrives and begins an immediate scan of the road beyond.",
        "{name} steps up and takes the watch.",
    ],
    "annatto": [
        "{name} arrives, surveys the empty road, and settles in.",
        "{name} takes up position with quiet efficiency.",
        "{name} assumes the post at the Annatto Gate.",
    ],
    "victory": [
        "{name} takes position at the Victory Gate.",
        "{name} arrives silently and assumes the watch.",
        "{name} settles into place at the Victory Gate.",
    ],
}


class NPCManager:
    """Manages all NPC instances in the game world."""

    def __init__(self, server):
        self.server = server
        self._npcs: Dict[int, NPC]            = {}   # npc_id  -> NPC
        self._room_npcs: Dict[int, List[int]] = {}   # room_id -> [npc_ids]
        self._template_to_id: Dict[str, int]  = {}   # template_id -> npc_id

        # Shift tracking
        self._shift_phase:  Dict[str, int]          = {}
        self._shift_guards: Dict[str, Dict[int, int]] = {}
        self._last_shift_time = time.time()

        # Stats for logging
        self._lua_count    = 0
        self._sql_count    = 0
        self._legacy_count = 0
        self._skipped_invalid_room = 0

    # ── Initialisation ────────────────────────────────────────────────────────

    async def initialize(self):
        """Load all NPC templates, restore SQL state, spawn into world."""
        scripts_path = self.server.config.get("paths.scripts", "./scripts")

        # ── Phase 1: Lua NPC files (authoritative) ────────────────────────────
        lua_templates = load_all_npc_luas(scripts_path)
        self._lua_count = len(lua_templates)

        # ── Phase 2: SQL registry (room overrides + alive state) ─────────────
        sql_state = self._load_sql_state()
        self._sql_count = len(sql_state)

        # ── Phase 3: Legacy hardcoded templates (NPC_TEMPLATES in npc_data.py) ─
        all_templates: Dict[str, dict] = {}
        for t in NPC_TEMPLATES:
            tid = t.get("template_id", "")
            if tid and tid not in lua_templates:
                all_templates[tid] = t
                self._legacy_count += 1

        # Lua wins on collision
        all_templates.update(lua_templates)

        # Apply SQL room overrides to templates
        for tid, state in sql_state.items():
            if tid in all_templates and state.get("current_room_id"):
                all_templates[tid]["room_id"]      = state["current_room_id"]
                all_templates[tid]["home_room_id"]  = state["current_room_id"]

        # ── Phase 4: Spawn ────────────────────────────────────────────────────
        spawned = skipped_relief = skipped_rare = skipped_dead = 0

        for tid, template in all_templates.items():
            # Skip if SQL says dead and not yet respawned
            state = sql_state.get(tid, {})
            if state and not state.get("is_alive", True):
                respawn_at = state.get("respawn_at", 0)
                if respawn_at > time.time():
                    skipped_dead += 1
                    continue

            # Relief guards don't spawn at startup — registered for shift system
            if not template.get("spawn_at_start", True):
                self._register_shift_guard(template, npc_instance=None)
                skipped_relief += 1
                continue

            # Rare spawn roll
            if template.get("rare_spawn", False):
                if random.random() > template.get("spawn_chance", 1.0):
                    skipped_rare += 1
                    continue

            template = self._normalize_template(template)
            if template is None:
                self._skipped_invalid_room += 1
                continue

            npc = NPC(template)
            self._attach_lua_runtime(npc, template)
            self._place_npc(npc)

            if npc.shift_id:
                self._register_shift_guard(template, npc_instance=npc)

            spawned += 1

        log.info(
            "NPCManager initialized: %d spawned (%d Lua, %d SQL overrides, %d legacy) "
            "%d relief pending, %d rare skipped, %d dead/respawning, %d invalid-room skipped",
            spawned, self._lua_count, self._sql_count, self._legacy_count,
            skipped_relief, skipped_rare, skipped_dead, self._skipped_invalid_room,
        )

    # ── SQL state ─────────────────────────────────────────────────────────────

    def _load_sql_state(self) -> dict:
        """Load npc_state table. Returns {template_id: state_dict}."""
        db = getattr(self.server, "db", None)
        if not db:
            return {}
        try:
            conn = db._get_conn()
            cur  = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT template_id, is_alive, current_room_id, respawn_at "
                "FROM npc_state"
            )
            rows = cur.fetchall()
            conn.close()
            return {r["template_id"]: r for r in rows}
        except Exception as e:
            log.warning("NPCManager: could not load npc_state: %s", e)
            return {}

    def _save_npc_state(self, npc: NPC):
        """Upsert one row in npc_state."""
        db = getattr(self.server, "db", None)
        if not db:
            return
        try:
            db.execute_update(
                """INSERT INTO npc_state (template_id, is_alive, current_room_id, respawn_at)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                       is_alive=VALUES(is_alive),
                       current_room_id=VALUES(current_room_id),
                       respawn_at=VALUES(respawn_at)""",
                (
                    npc.template_id,
                    1 if npc.alive else 0,
                    npc.room_id,
                    int(npc.death_time + npc.respawn_seconds) if not npc.alive else 0,
                )
            )
        except Exception as e:
            log.warning("NPCManager: npc_state save failed for %s: %s", npc.template_id, e)

    def _room_exists(self, room_id: int) -> bool:
        try:
            return bool(room_id) and self.server.world.get_room(int(room_id)) is not None
        except Exception:
            return False

    def _normalize_template(self, template: dict) -> Optional[dict]:
        normalized = dict(template)

        home_room = int(normalized.get("home_room_id") or normalized.get("room_id") or 0)
        patrol_rooms = []
        for room_id in normalized.get("patrol_rooms", []) or []:
            try:
                room_id = int(room_id)
            except (TypeError, ValueError):
                continue
            if self._room_exists(room_id) and room_id not in patrol_rooms:
                patrol_rooms.append(room_id)

        if not self._room_exists(home_room):
            if patrol_rooms:
                home_room = patrol_rooms[0]
            else:
                label = normalized.get("lua_file") or normalized.get("template_id", "unknown_npc")
                log.debug("Skipping NPC %s due to invalid home room id %s", label, normalized.get("home_room_id"))
                return None

        normalized["home_room_id"] = home_room
        normalized["room_id"] = home_room
        normalized["patrol_rooms"] = patrol_rooms

        if normalized.get("can_wander") and len(patrol_rooms) < 2:
            normalized["can_wander"] = False

        return normalized

    def _attach_lua_runtime(self, npc: NPC, template: dict):
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        if not engine or not engine.available:
            return

        lua_module = template.get("lua_module")
        lua_file = template.get("lua_file")
        try:
            if lua_file and os.path.exists(lua_file):
                npc._lua_table = engine.load_file(lua_file)
            elif lua_module:
                npc._lua_table = engine.require(lua_module)
        except Exception as e:
            log.error("NPC Lua load failed (%s): %s", npc.template_id, e)
            npc._lua_table = None
            return

        if npc._lua_table and npc.has_hook("on_load"):
            try:
                engine.call_hook(npc._lua_table, "on_load")
            except Exception as e:
                log.error("NPC on_load hook error (%s): %s", npc.template_id, e)

    # ── World index helpers ────────────────────────────────────────────────────

    def _place_npc(self, npc: NPC):
        self._npcs[npc.id] = npc
        self._template_to_id[npc.template_id] = npc.id
        self._room_npcs.setdefault(npc.room_id, []).append(npc.id)

    def _remove_npc(self, npc: NPC):
        self._npcs.pop(npc.id, None)
        self._template_to_id.pop(npc.template_id, None)
        room_list = self._room_npcs.get(npc.room_id, [])
        if npc.id in room_list:
            room_list.remove(npc.id)

    def _move_npc_index(self, npc: NPC, new_room_id: int):
        """Update the room index only — does not broadcast."""
        old_room = npc.room_id
        room_list = self._room_npcs.get(old_room, [])
        if npc.id in room_list:
            room_list.remove(npc.id)
        npc.room_id           = new_room_id
        npc.current_room_id   = new_room_id
        self._room_npcs.setdefault(new_room_id, []).append(npc.id)

    # ── Query helpers ─────────────────────────────────────────────────────────

    def get_npcs_in_room(self, room_id: int) -> List[NPC]:
        return [self._npcs[nid] for nid in self._room_npcs.get(room_id, [])
                if nid in self._npcs]

    def find_npc_in_room(self, room_id: int, name_fragment: str) -> Optional[NPC]:
        name_lower = name_fragment.lower()
        for npc in self.get_npcs_in_room(room_id):
            if name_lower in npc.name.lower():
                return npc
        return None

    def get_shopkeeper_in_room(self, room_id: int) -> Optional[NPC]:
        for npc in self.get_npcs_in_room(room_id):
            if npc.can_shop and npc.shop_id:
                return npc
        return None

    def get_npc(self, npc_id: int) -> Optional[NPC]:
        return self._npcs.get(npc_id)

    def get_npc_by_template(self, template_id: str) -> Optional[NPC]:
        nid = self._template_to_id.get(template_id)
        return self._npcs.get(nid) if nid else None

    def get_service_npc_in_room(self, room_id: int, service_tag: str) -> Optional[NPC]:
        for npc in self.get_npcs_in_room(room_id):
            if npc.matches_service(service_tag):
                return npc
        return None

    def is_unkillable(self, npc_id: int) -> bool:
        npc = self._npcs.get(npc_id)
        return npc is not None and npc.unkillable

    def get_all_npcs(self) -> List[NPC]:
        return list(self._npcs.values())

    # ── Main tick ─────────────────────────────────────────────────────────────

    async def tick(self, tick_count: int):
        """Called every game tick (10/sec)."""

        # Ambient emotes + chat — every 5 seconds (50 ticks)
        if tick_count % 50 == 0:
            await self._emote_tick()
            await self._chat_tick()

        # Patrol movement — every 1 second (10 ticks)
        if tick_count % 10 == 0:
            await self._patrol_tick()
            await self._hook_tick()

        # Combat AI — every 1 second
        if tick_count % 10 == 0:
            await self._combat_tick()

        # Loot scan — every 10 seconds (100 ticks)
        if tick_count % 100 == 0:
            await self._loot_tick()

        # Bot AI — every 10 seconds
        if tick_count % 100 == 0:
            await self._bot_tick()

        # Respawn check — every 60 seconds (600 ticks)
        if tick_count % 600 == 0:
            await self._respawn_tick()

        # Guard shifts — every 60 seconds
        if tick_count % 600 == 0:
            await self._shift_tick()

    # ── Emote tick ────────────────────────────────────────────────────────────

    async def _emote_tick(self):
        for npc in list(self._npcs.values()):
            if not npc.can_emote:
                continue
            emote = npc.get_ambient_emote()
            if emote:
                await self.server.world.broadcast_to_room(npc.room_id, emote)

    # ── Chat tick ─────────────────────────────────────────────────────────────

    async def _chat_tick(self):
        for npc in list(self._npcs.values()):
            if not npc.can_chat:
                continue
            line = npc.get_chat_line()
            if line:
                await self.server.world.broadcast_to_room(npc.room_id, line)

    # ── Patrol tick ───────────────────────────────────────────────────────────

    async def _patrol_tick(self):
        for npc in list(self._npcs.values()):
            if not npc.can_wander or not npc.patrol_rooms:
                continue
            if not npc.is_ready_to_move():
                continue
            if random.random() > npc.wander_chance:
                npc.record_move()
                continue
            next_room = npc.get_next_patrol_room()
            if next_room and next_room != npc.room_id:
                await self._move_npc(npc, next_room)

    async def _hook_tick(self):
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        if not engine or not engine.available:
            return

        for npc in list(self._npcs.values()):
            if not npc.alive or not npc.has_hook("on_tick") or not npc._lua_table:
                continue
            try:
                engine.call_hook(npc._lua_table, "on_tick")
            except Exception as e:
                log.error("NPC on_tick hook error (%s): %s", npc.template_id, e)

    async def _move_npc(self, npc: NPC, target_room_id: int):
        old_room  = npc.room_id
        direction = self._get_direction(old_room, target_room_id)

        if direction:
            depart_msg = npc_emote(
                f"{npc.display_name} {_DEPARTURE_BY_DIR.get(direction, 'heads off.')}"
            )
            arrive_msg = npc_emote(
                f"{npc.display_name} {_ARRIVAL_BY_DIR.get(direction, 'arrives.')}"
            )
        else:
            depart_msg = npc_emote(f"{npc.display_name} heads off.")
            arrive_msg = npc_emote(f"{npc.display_name} arrives.")

        self._move_npc_index(npc, target_room_id)
        npc.record_move()

        await self.server.world.broadcast_to_room(old_room,        depart_msg)
        await self.server.world.broadcast_to_room(target_room_id,  arrive_msg)

    def _get_direction(self, from_room: int, to_room: int) -> Optional[str]:
        try:
            world = self.server.world
            if hasattr(world, "get_direction_between"):
                return world.get_direction_between(from_room, to_room)
        except Exception:
            pass
        return None

    # ── Combat tick ───────────────────────────────────────────────────────────

    async def _combat_tick(self):
        """
        Combat-capable NPCs that are in_combat fire an attack via CombatEngine.
        Aggressive NPCs that are not in combat scan their room for targets.
        """
        combat = getattr(self.server, "combat", None)
        if not combat:
            return

        for npc in list(self._npcs.values()):
            if not npc.can_combat or not npc.alive:
                continue

            # In combat — attack target
            if npc.in_combat and npc.target:
                target = npc.target
                # Target may be a player session or a creature
                if getattr(target, "is_dead", False) or not getattr(target, "alive", True):
                    npc.in_combat = False
                    npc.target    = None
                    continue
                if npc.can_act():
                    try:
                        await combat.creature_attacks_player(npc, target)
                    except Exception as e:
                        log.error("NPC combat error (%s): %s", npc.template_id, e)

            # Aggressive and idle — scan for targets in the same room
            elif npc.aggressive and not npc.in_combat:
                players = self.server.world.get_players_in_room(npc.room_id)
                if players:
                    target = random.choice(players)
                    npc.in_combat = True
                    npc.target    = target
                    await self.server.world.broadcast_to_room(
                        npc.room_id,
                        colorize(
                            f"{npc.display_name} turns with hostile intent!",
                            TextPresets.COMBAT_DAMAGE_TAKEN
                        )
                    )

    # ── Loot tick ─────────────────────────────────────────────────────────────

    async def _loot_tick(self):
        """
        Loot-capable NPCs collect silver from dead creatures in their room.
        (Item/gem looting is a stub for the inventory system to hook into.)
        """
        creature_mgr = getattr(self.server, "creatures", None)
        if not creature_mgr:
            return

        for npc in list(self._npcs.values()):
            if not npc.can_loot or not npc.alive:
                continue

            dead = [c for c in creature_mgr.get_creatures_in_room(npc.room_id)
                    if c.is_dead and getattr(c, "treasure", {}).get("coins")]
            if not dead and npc.loot_radius > 0:
                # Check adjacent rooms if radius allows
                room = self.server.world.get_room(npc.room_id)
                if room:
                    for _, adj_id in list(room.exits.items())[:npc.loot_radius]:
                        dead += [c for c in creature_mgr.get_creatures_in_room(adj_id)
                                 if c.is_dead and getattr(c, "treasure", {}).get("coins")]

            for corpse in dead:
                # Collect silver — move it to the NPC (cosmetic for now)
                silver = getattr(corpse, "loot_silver", random.randint(1, 20))
                await self.server.world.broadcast_to_room(
                    npc.room_id,
                    npc_emote(
                        f"{npc.display_name} quickly pockets some silver from "
                        f"the remains of {getattr(corpse, 'full_name', 'a creature')}."
                    )
                )
                # Clear coin loot so no double-collect
                if hasattr(corpse, "treasure") and isinstance(corpse.treasure, dict):
                    corpse.treasure["coins"] = False

    # ── Bot tick ──────────────────────────────────────────────────────────────

    async def _bot_tick(self):
        """
        Bot NPCs: if injured below flee threshold, move toward rest room.
        Full bot hunting/shopping/chatting is a later stage.
        """
        for npc in list(self._npcs.values()):
            if not npc.is_bot or not npc.alive:
                continue

            hp_pct = npc.health_current / npc.health_max if npc.health_max > 0 else 1.0
            if hp_pct < npc.bot_hp_flee and npc.bot_rest_room and npc.room_id != npc.bot_rest_room:
                await self._move_npc_toward(npc, npc.bot_rest_room)

    async def _move_npc_toward(self, npc: NPC, target_room_id: int):
        """Move one step toward target_room_id using world pathfinding."""
        world = self.server.world
        if not hasattr(world, "find_path"):
            return
        path = world.find_path(npc.room_id, target_room_id)
        if path and len(path) >= 2:
            await self._move_npc(npc, path[1])

    # ── Respawn tick ──────────────────────────────────────────────────────────

    async def _respawn_tick(self):
        """Check dead NPCs and respawn those whose timer has expired."""
        now = time.time()
        for npc in list(self._npcs.values()):
            if npc.alive:
                continue
            if npc.respawn_seconds <= 0:
                continue
            if now - npc.death_time < npc.respawn_seconds:
                continue

            # Respawn
            npc.health_current = npc.health_max
            npc.alive          = True
            npc.is_alive       = True
            npc.in_combat      = False
            npc.target         = None
            npc.wounds         = {}
            npc.status_effects = {}
            npc.death_time     = 0.0

            # Return to home room
            if npc.room_id != npc.home_room_id:
                self._move_npc_index(npc, npc.home_room_id)

            await self.server.world.broadcast_to_room(
                npc.room_id,
                npc_emote(f"{npc.display_name} arrives.")
            )
            self._save_npc_state(npc)
            log.info("NPC respawned: %s in room %d", npc.template_id, npc.room_id)

    # ── Guard shift system ────────────────────────────────────────────────────

    def _register_shift_guard(self, template: dict, npc_instance: Optional[NPC]):
        sid   = template.get("shift_id")
        phase = int(template.get("shift_phase", 0))
        if not sid:
            return
        if sid not in self._shift_guards:
            self._shift_guards[sid] = {}
            self._shift_phase[sid]  = 0
        if npc_instance:
            self._shift_guards[sid][phase] = npc_instance.id
        else:
            self._shift_guards[sid][phase] = template

    async def _shift_tick(self):
        now = time.time()
        if now - self._last_shift_time < SHIFT_INTERVAL:
            return
        self._last_shift_time = now
        log.info("Guard shift change initiated.")
        for shift_id, guard_map in self._shift_guards.items():
            await self._do_shift_change(shift_id, guard_map)

    async def _do_shift_change(self, shift_id: str, guard_map: dict):
        current_phase  = self._shift_phase.get(shift_id, 0)
        incoming_phase = 1 - current_phase

        outgoing_entry = guard_map.get(current_phase)
        incoming_entry = guard_map.get(incoming_phase)
        if outgoing_entry is None or incoming_entry is None:
            return

        outgoing_npc = (self._npcs.get(outgoing_entry)
                        if isinstance(outgoing_entry, int) else None)

        if isinstance(incoming_entry, int):
            incoming_npc = self._npcs.get(incoming_entry)
        elif isinstance(incoming_entry, dict):
            incoming_npc = NPC(incoming_entry)
            if outgoing_npc:
                incoming_npc.room_id      = outgoing_npc.room_id
                incoming_npc.home_room_id = outgoing_npc.home_room_id
            self._place_npc(incoming_npc)
            guard_map[incoming_phase] = incoming_npc.id
        else:
            incoming_npc = None

        if not outgoing_npc or not incoming_npc:
            return

        gate_room = outgoing_npc.room_id

        depart_lines = _SHIFT_DEPARTURE_LINES.get(shift_id, ["{name} departs."])
        arrive_lines = _SHIFT_ARRIVAL_LINES.get(shift_id,  ["{name} arrives."])
        depart_msg = npc_emote(random.choice(depart_lines).replace("{name}", outgoing_npc.name))
        arrive_msg = npc_emote(random.choice(arrive_lines).replace("{name}", incoming_npc.name))

        await self.server.world.broadcast_to_room(gate_room, depart_msg)
        self._remove_npc(outgoing_npc)

        self._move_npc_index(incoming_npc, gate_room)
        await self.server.world.broadcast_to_room(gate_room, arrive_msg)

        self._shift_phase[shift_id] = incoming_phase
        log.info("Shift change at %s gate: %s out, %s in.",
                 shift_id, outgoing_npc.name, incoming_npc.name)

    # ── Event hooks ───────────────────────────────────────────────────────────

    async def on_player_enter_room(self, session, room_id: int):
        """Called by movement handler when a player enters a room."""
        for npc in self.get_npcs_in_room(room_id):
            # Greeting
            greeting_text = npc.get_greeting_text()
            if greeting_text:
                greeting = greeting_text.replace("{player}", session.character_name)
                await session.send_line(npc_emote(f"{npc.display_name} {greeting}"))

            # Lua hook: on_player_enter
            if npc.has_hook("on_player_enter") and npc._lua_table:
                try:
                    lua = getattr(self.server, "lua", None)
                    engine = getattr(lua, "engine", None) if lua else None
                    if engine and engine.available:
                        engine.call_hook(npc._lua_table, "on_player_enter", session)
                except Exception as e:
                    log.error("NPC on_player_enter hook error (%s): %s",
                              npc.template_id, e)

    async def on_npc_death(self, npc: NPC, killer=None):
        """
        Called when an NPC is killed (by player or creature).
        Handles loot drop, death message, state save, hook.
        """
        npc.alive    = False
        npc.is_alive = False
        npc.in_combat = False
        npc.target    = None
        npc.death_time = time.time()
        npc.status_effects = {}

        await self.server.world.broadcast_to_room(
            npc.room_id,
            colorize(
                f"  {npc.display_name} collapses lifelessly.",
                TextPresets.COMBAT_DEATH
            )
        )

        # Lua hook: on_death
        if npc.has_hook("on_death") and npc._lua_table:
            try:
                lua    = getattr(self.server, "lua", None)
                engine = getattr(lua, "engine", None) if lua else None
                if engine and engine.available:
                    engine.call_hook(npc._lua_table, "on_death")
            except Exception as e:
                log.error("NPC on_death hook error (%s): %s", npc.template_id, e)

        self._save_npc_state(npc)

    async def fire_invasion_hook(self, zone_slug: str):
        """Called by the invasion manager when an invasion begins in a zone."""
        for npc in list(self._npcs.values()):
            if not npc.is_invasion:
                continue
            if npc.invasion_zone and npc.invasion_zone != zone_slug:
                continue
            if npc.has_hook("on_invasion") and npc._lua_table:
                try:
                    lua    = getattr(self.server, "lua", None)
                    engine = getattr(lua, "engine", None) if lua else None
                    if engine and engine.available:
                        engine.call_hook(npc._lua_table, "on_invasion", zone_slug)
                except Exception as e:
                    log.error("NPC on_invasion hook error (%s): %s", npc.template_id, e)

    # ── Player flag helpers (quest / relationship state) ──────────────────────

    def get_player_flag(self, template_id: str, character_id: int, flag: str) -> str:
        """Read a per-player flag from the DB. Returns '' if not set."""
        db = getattr(self.server, "db", None)
        if not db:
            return ""
        try:
            conn = db._get_conn()
            cur  = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT flag_value FROM npc_player_flags "
                "WHERE template_id=%s AND character_id=%s AND flag_name=%s",
                (template_id, character_id, flag)
            )
            row = cur.fetchone()
            conn.close()
            return row["flag_value"] if row else ""
        except Exception:
            return ""

    def set_player_flag(self, template_id: str, character_id: int, flag: str, value: str):
        """Write a per-player flag to the DB."""
        db = getattr(self.server, "db", None)
        if not db:
            return
        try:
            db.execute_update(
                """INSERT INTO npc_player_flags (template_id, character_id, flag_name, flag_value)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE flag_value=VALUES(flag_value)""",
                (template_id, character_id, flag, value)
            )
        except Exception as e:
            log.warning("set_player_flag failed (%s/%s/%s): %s",
                        template_id, character_id, flag, e)
