"""
CreatureManager - Spawns, tracks, despawns, and AI-ticks all creatures.

HOW SPAWNS WORK
---------------
Every zone's  scripts/zones/<zone>/mobs/<creature>.lua  defines:

    Creature.spawn_rooms  = { <room_id>, ... }
    Creature.roam_rooms   = { <room_id>, ... }
    Creature.max_count    = N
    Creature.respawn_seconds = N

The lua_mob_loader scans ALL zones at startup automatically.
To add a new creature: create a Lua file in the appropriate zone mobs/ folder.
There is NO hardcoded creature or spawn data in Python — Lua is the only source.
"""

import asyncio
import concurrent.futures
import os
import random
import re
import time
import logging
from collections import deque
from typing import Dict, List, Optional

from server.core.entity.creature.ai_runtime import (
    apply_passive_behavior,
    attempt_special_action,
    pack_follow_candidates,
    recompute_group_modifiers,
    sniff_bonus,
)
from server.core.entity.creature.creature import Creature
from server.core.entity.creature.creature_planner import plan_creature_actions
from server.core.entity.creature.creature_data import get_template, get_all_templates, register_templates
from server.core.entity.creature.lua_mob_loader import load_all_mob_luas
from server.core.entity.creature.lua_spawn_registry_loader import load_zone_spawn_registries
from server.core.engine.magic_effects import has_effect
from server.core.protocol.colors import creature_name, creature_arrival, creature_departure, colorize, TextPresets

log = logging.getLogger(__name__)

_ORDINAL_TARGET_RE = re.compile(r"^\s*(\d+)(?:st|nd|rd|th)?\s+(.+?)\s*$", re.IGNORECASE)


class CreatureManager:
    """Manages all creature instances in the game world."""

    def __init__(self, server):
        self.server = server
        self._creatures: Dict[int, Creature] = {}
        self._room_creatures: Dict[int, List[int]] = {}
        self._dead_creatures: List[Creature] = []
        self._spawn_config: List[dict] = []
        self._hunting_rooms: set = set()
        self._zone_level_spawn_threshold = 10
        self._spawn_registries: dict = {}
        self._spawn_registry_blocks: dict = {}
        self._settings: dict = {
            "active_player_bubble_rooms": 60,
            "planner_workers": 0,
            "planner_queue_multiplier": 2,
            "planner_submit_interval_ticks": 30,
            "wander_submit_interval_ticks": 150,
            "perf_log_interval_seconds": 60,
        }
        self._planner_pool = None
        self._planner_future = None
        self._perf = {"planner_submit": 0, "planner_done": 0}
        self._last_perf_log_at = 0.0

    # ── Initialization ────────────────────────────────────────────────────

    async def initialize(self):
        if getattr(self.server, "lua", None):
            self.server.lua.get_ucs_cfg()
            spawn_settings = self.server.lua.get_creature_spawns() or {}
            self._settings = dict((spawn_settings.get("defaults") or {}))
        self._init_planner_pool()
        self._last_perf_log_at = time.time()
        scripts_path = self.server.config.get("paths.scripts", "./scripts")
        self._spawn_registries = load_zone_spawn_registries(scripts_path)

        # ── Phase 1: Lua mob files (authoritative for scripted creatures) ──
        lua_templates = load_all_mob_luas(scripts_path)
        lua_registered = register_templates(lua_templates)
        log.info("CreatureManager: registered %d Lua mob templates", lua_registered)

        # ── Phase 2: SQL creatures + spawn_points (additive, never cancels Lua) ──
        sql_configs = self._load_sql_spawn_configs()

        # ── Phase 3: Build unified spawn configs from ALL sources ──────────
        self._build_spawn_configs(lua_templates, sql_configs, self._spawn_registries)

        # ── Phase 4: Initial spawn ────────────────────────────────────────
        bubble_rooms = self._active_player_bubble()
        spawned = 0
        if bubble_rooms:
            for config in self._spawn_config:
                template = get_template(config["template_id"])
                candidate_rooms = [room_id for room_id in (config["rooms"] or []) if int(room_id or 0) in bubble_rooms]
                if not template or not candidate_rooms:
                    continue
                desired = self._desired_population_for_config(config)
                for _ in range(desired):
                    room_id = random.choice(candidate_rooms)
                    if self.spawn_creature(config["template_id"], room_id):
                        spawned += 1

        log.info(
            "CreatureManager initialized: %d creatures spawned, %d configs "
            "(%d Lua, %d SQL), %d hunting rooms",
            spawned, len(self._spawn_config),
            self._lua_config_count, self._sql_config_count,
            len(self._hunting_rooms)
        )

    def shutdown(self):
        pool = self._planner_pool
        self._planner_pool = None
        self._planner_future = None
        if pool:
            try:
                pool.shutdown(wait=False, cancel_futures=True)
            except Exception:
                log.debug("Creature planner pool shutdown failed", exc_info=True)

    def _init_planner_pool(self):
        workers = max(0, int(self._settings.get("planner_workers") or 0))
        if workers <= 0:
            self._planner_pool = None
            return
        cpu_total = max(1, int(os.cpu_count() or 1))
        workers = max(1, min(workers, max(1, cpu_total - 1)))
        self._planner_pool = concurrent.futures.ProcessPoolExecutor(max_workers=workers)
        log.info("CreatureManager planner pool ready (%d worker processes)", workers)

    # ── SQL creature loader ─────────────────────────────────────────────────

    def _load_sql_spawn_configs(self):
        """
        Load creatures from the SQL creatures + spawn_points tables.
        Returns a list of spawn config dicts ready for _build_spawn_configs.

        SQL creatures that don't already have a registered template get
        auto-registered so they work with the same combat/wound/aim systems.
        """
        db = getattr(self.server, "db", None)
        if not db or not db._pool:
            log.info("CreatureManager: no DB — skipping SQL creature load")
            return []

        try:
            conn = db._get_conn()
        except Exception as e:
            log.error("CreatureManager: DB conn failed for SQL creatures: %s", e)
            return []

        sql_configs = []
        try:
            cur = conn.cursor(dictionary=True)

            # Pull every spawn_point row joined with its creature definition
            cur.execute("""
                SELECT
                    sp.room_id,
                    sp.creature_id,
                    sp.max_count,
                    sp.respawn_seconds,
                    sp.is_enabled,
                    c.name,
                    c.article,
                    c.level,
                    c.creature_type,
                    c.health_max,
                    c.attack_strength,
                    c.defense_strength,
                    c.casting_strength,
                    c.target_defense,
                    c.action_timer,
                    c.behavior_script,
                    c.is_aggressive,
                    c.can_cast,
                    c.can_maneuver,
                    c.is_undead,
                    c.body_type,
                    c.experience_value,
                    c.silver_min,
                    c.silver_max,
                    c.loot_table_id,
                    c.skin_noun,
                    c.description,
                    c.death_message
                FROM spawn_points sp
                JOIN creatures c ON sp.creature_id = c.id
                WHERE sp.is_enabled = 1
                ORDER BY sp.creature_id, sp.room_id
            """)

            # Group spawn_points by creature_id
            from collections import defaultdict
            creature_rooms = defaultdict(list)       # creature_id -> [(room_id, max_count, respawn)]
            creature_data  = {}                       # creature_id -> row dict

            for row in cur.fetchall():
                cid = int(row["creature_id"])
                creature_rooms[cid].append({
                    "room_id":         int(row["room_id"]),
                    "max_count":       int(row.get("max_count", 1) or 1),
                    "respawn_seconds": int(row.get("respawn_seconds", 300) or 300),
                })
                if cid not in creature_data:
                    creature_data[cid] = row

            log.info("CreatureManager: SQL spawn_points loaded %d creatures across %d rooms",
                     len(creature_data), sum(len(v) for v in creature_rooms.values()))

            # Build template + spawn config for each SQL creature
            for cid, rooms_list in creature_rooms.items():
                row = creature_data[cid]
                name = row["name"]

                # Derive a template_id from the SQL name (same convention as Lua loader)
                template_id = name.lower().replace(" ", "_").replace("'", "")

                # Auto-register as a template if not already in the registry
                existing = get_template(template_id)
                if not existing:
                    article = row.get("article", "a") or "a"
                    level = int(row.get("level", 1) or 1)
                    body_type = row.get("body_type", "biped") or "biped"
                    as_val = int(row.get("attack_strength", level * 5 + 20) or (level * 5 + 20))
                    ds_val = int(row.get("defense_strength", level * 3 + 10) or (level * 3 + 10))
                    cs_val = int(row.get("casting_strength", 0) or 0)
                    td_val = int(row.get("target_defense", level * 3) or (level * 3))
                    hp_val = int(row.get("health_max", 50) or 50)

                    classification = "living"
                    if row.get("is_undead"):
                        classification = "corporeal_undead"

                    tmpl = {
                        "template_id":    template_id,
                        "name":           name,
                        "article":        article,
                        "level":          level,
                        "hp":             hp_val,
                        "hp_variance":    max(1, hp_val // 10),
                        "as_melee":       as_val,
                        "ds_melee":       ds_val,
                        "ds_ranged":      ds_val,
                        "ds_bolt":        int(row.get("casting_strength", 0) or 0),
                        "td":             td_val,
                        "udf":            0,
                        "armor_asg":      1,
                        "armor_natural":  True,
                        "cva":            0,
                        "damage_type":    "crush",
                        "body_type":      body_type,
                        "family":         "",
                        "classification": classification,
                        "description":    row.get("description", "") or "",
                        "attacks":        [{
                            "name": "attack", "as": as_val, "damage_type": "crush",
                            "verb_first": "attacks you",
                            "verb_third": "attacks {target}",
                            "roundtime": 5,
                        }],
                        "spells":         [],
                        "abilities":      [],
                        "immune":         [],
                        "resist":         [],
                        "special_loot":   [],
                        "skin":           row.get("skin_noun", None),
                        "treasure":       {
                            "coins": int(row.get("silver_max", 0) or 0) > 0,
                            "gems":  False,
                            "magic": bool(row.get("can_cast")),
                            "boxes": False,
                        },
                        "decay_seconds":  300,
                        "crumbles":       False,
                        "decay_message":  row.get("death_message", "") or "",
                        "spawn_rooms":    [],
                        "wander_rooms":   [],
                        "respawn_time":   300,
                        "max_count":      1,
                        "aggressive":     bool(row.get("is_aggressive", True)),
                        "wander_chance":  0.2,
                        "pursue_chance":  0.3,
                    }
                    # Register it — this does NOT conflict with Lua templates
                    # because register_templates already handled Lua overrides.
                    # This only adds creatures that exist ONLY in SQL.
                    from server.core.entity.creature.creature_data import CREATURE_TEMPLATES
                    CREATURE_TEMPLATES[template_id] = tmpl
                    log.info("  SQL auto-registered template '%s' (creature_id=%d)", template_id, cid)

                # Collect all room IDs and the max max_count for this creature
                all_rooms = [r["room_id"] for r in rooms_list]
                total_max = sum(r["max_count"] for r in rooms_list)
                respawn   = min(r["respawn_seconds"] for r in rooms_list)

                sql_configs.append({
                    "template_id":      template_id,
                    "max_count":        total_max,
                    "rooms":            all_rooms,
                    "wander":           all_rooms,
                    "respawn_seconds":  respawn,
                    "source":           "sql",
                })

        except Exception as e:
            log.error("CreatureManager: failed to load SQL spawn configs: %s", e, exc_info=True)
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return sql_configs

    # ── Unified spawn config builder ─────────────────────────────────────

    def _zone_slug_for_room(self, room_id: int) -> Optional[str]:
        room = self.server.world.get_room(room_id)
        if not room:
            return None
        zone = self.server.world.get_zone_by_id(int(getattr(room, "zone_id", 0) or 0))
        return getattr(zone, "slug", None) if zone else None

    def _record_spawn_registry_block(self, template_id: str, room_id: int, zone_slug: str):
        entry = self._spawn_registry_blocks.setdefault(template_id, {
            "rooms": set(),
            "zones": set(),
        })
        entry["rooms"].add(int(room_id))
        if zone_slug:
            entry["zones"].add(str(zone_slug))

    def _room_allowed_by_spawn_registry(self, template_id: str, template: dict, room_id: int, registries: dict) -> bool:
        try:
            level = int((template or {}).get("level", 1) or 1)
        except Exception:
            level = 1
        if level > 35:
            return True

        zone_slug = self._zone_slug_for_room(room_id)
        if not zone_slug:
            return True

        registry = (registries or {}).get(zone_slug)
        if not registry:
            return True

        population = registry.get("population") or {}
        map_locked = bool(registry.get("map_locked", False))
        population_entry = population.get(template_id)
        mob_rooms = registry.get("mob_rooms") or {}
        depth_rooms = registry.get("depth_rooms") or {}

        if template_id in mob_rooms:
            allowed = set(int(r) for r in (mob_rooms.get(template_id) or []))
            if room_id in allowed:
                return True
            self._record_spawn_registry_block(template_id, room_id, zone_slug)
            return False

        if population_entry:
            depth_key = str(population_entry.get("depth", "") or "").strip()
            if depth_key and depth_key in depth_rooms:
                allowed = set(int(r) for r in (depth_rooms.get(depth_key) or []))
                if room_id in allowed:
                    return True
                self._record_spawn_registry_block(template_id, room_id, zone_slug)
                return False
            if map_locked:
                return True
            return True

        origin = str((template or {}).get("template_origin", "") or "").strip().lower()
        if not map_locked:
            return True

        if origin == "catalog":
            self._record_spawn_registry_block(template_id, room_id, zone_slug)
            return False

        source_zones = {
            str(zone).strip()
            for zone in ((template or {}).get("source_zones") or [])
            if str(zone).strip()
        }
        source_zone = str((template or {}).get("source_zone", "") or "").strip()
        if source_zone:
            source_zones.add(source_zone)

        if origin == "authored" and zone_slug in source_zones:
            return True

        if origin == "authored":
            self._record_spawn_registry_block(template_id, room_id, zone_slug)
            return False

        return True

    def _build_spawn_configs(self, lua_templates: dict, sql_configs: list = None, spawn_registries: dict = None):
        world = self.server.world
        configs = []
        hunting = set()
        self._spawn_registry_blocks = {}

        lua_count = 0
        sql_count = 0

        # ── Lua-driven spawns ──────────────────────────────────────────────
        for tid, tmpl in lua_templates.items():
            spawn_rooms  = tmpl.get("spawn_rooms", [])
            wander_rooms = tmpl.get("wander_rooms", [])
            max_count    = tmpl.get("max_count", 3)
            if not spawn_rooms:
                continue

            valid_spawn = [
                r for r in spawn_rooms
                if isinstance(r, int)
                and world.get_room(r)
                and not world.get_room(r).safe
                and self._room_allowed_by_spawn_registry(tid, tmpl, r, spawn_registries)
            ]
            valid_wander = [
                r for r in wander_rooms
                if isinstance(r, int)
                and world.get_room(r)
                and not world.get_room(r).safe
                and self._room_allowed_by_spawn_registry(tid, tmpl, r, spawn_registries)
            ]
            if not valid_spawn:
                continue

            configs.append({
                "template_id": tid,
                "max_count":   max_count,
                "base_max_count": max_count,
                "template_level": int(tmpl.get("level", 1) or 1),
                "rooms":       valid_spawn,
                "wander":      valid_wander,
                "zone_ids":    sorted({int(self.server.world.get_room(r).zone_id) for r in valid_spawn if self.server.world.get_room(r)}),
                "source":      "lua",
            })
            hunting.update(valid_spawn)
            hunting.update(valid_wander)
            lua_count += 1

        # ── SQL-driven spawns (additive — never cancels Lua) ──────────────
        if sql_configs:
            for cfg in sql_configs:
                room_ids = cfg.get("rooms", [])
                valid_spawn = [
                    r for r in room_ids
                    if isinstance(r, int) and world.get_room(r) and not world.get_room(r).safe
                ]
                if not valid_spawn:
                    continue

                configs.append({
                    "template_id": cfg["template_id"],
                    "max_count":   cfg.get("max_count", 1),
                    "base_max_count": cfg.get("max_count", 1),
                    "template_level": int((get_template(cfg["template_id"]) or {}).get("level", 1) or 1),
                    "rooms":       valid_spawn,
                    "wander":      valid_spawn,
                    "zone_ids":    sorted({int(self.server.world.get_room(r).zone_id) for r in valid_spawn if self.server.world.get_room(r)}),
                    "source":      "sql",
                })
                hunting.update(valid_spawn)
                sql_count += 1

        self._spawn_config = configs
        self._hunting_rooms = hunting
        self._lua_config_count = lua_count
        self._sql_config_count = sql_count
        self._legacy_config_count = 0
        if self._spawn_registry_blocks:
            blocked_templates = len(self._spawn_registry_blocks)
            blocked_rooms = sum(len(info["rooms"]) for info in self._spawn_registry_blocks.values())
            offenders = sorted(
                self._spawn_registry_blocks.items(),
                key=lambda row: (-len(row[1]["rooms"]), row[0]),
            )[:10]
            for template_id, info in offenders:
                log.warning(
                    "Spawn registry blocked '%s' from %d room(s) across zone(s): %s",
                    template_id,
                    len(info["rooms"]),
                    ", ".join(sorted(info["zones"])) or "unknown",
                )
            log.info(
                "CreatureManager: spawn registry blocked %d template(s) across %d room(s) in map-backed zones",
                blocked_templates,
                blocked_rooms,
            )

    # ── Spawn helpers ─────────────────────────────────────────────────────

    def spawn_creature(self, template_id: str, room_id: int, *, allow_safe: bool = False, spawn_context: dict | None = None) -> Optional[Creature]:
        room = self.server.world.get_room(room_id)
        if room and room.safe and not allow_safe:
            log.warning("Blocked creature spawn in safe room %d", room_id)
            return None
        template = get_template(template_id)
        if not template:
            log.warning("Unknown creature template: %s", template_id)
            return None
        creature = Creature(template)
        creature.current_room_id = room_id
        creature.spawn_context = dict(spawn_context or {})
        self._creatures[creature.id] = creature
        self._room_creatures.setdefault(room_id, []).append(creature.id)
        return creature

    def remove_creature(self, creature: Creature):
        self._creatures.pop(creature.id, None)
        room_list = self._room_creatures.get(creature.current_room_id, [])
        try:
            room_list.remove(creature.id)
        except ValueError:
            pass

    def mark_dead(self, creature: Creature):
        creature.alive = creature.in_combat = False
        creature.target = None
        creature.death_time = time.time()
        self._dead_creatures.append(creature)

    def get_creatures_in_room(self, room_id: int) -> List[Creature]:
        return [
            self._creatures[cid]
            for cid in self._room_creatures.get(room_id, [])
            if cid in self._creatures and self._creatures[cid].alive
        ]

    def get_dead_creatures_in_room(self, room_id: int) -> List[Creature]:
        return [
            self._creatures[cid]
            for cid in self._room_creatures.get(room_id, [])
            if cid in self._creatures and self._creatures[cid].is_dead
        ]

    def get_creature(self, creature_id: int) -> Optional[Creature]:
        return self._creatures.get(creature_id)

    def find_creature_in_room(self, room_id: int, name_fragment: str) -> Optional[Creature]:
        name_lower = (name_fragment or "").strip().lower()
        if not name_lower:
            return None

        ordinal = 1
        m = _ORDINAL_TARGET_RE.match(name_lower)
        if m:
            ordinal = max(1, int(m.group(1)))
            name_lower = m.group(2).strip().lower()

        matches = [
            c for c in self.get_creatures_in_room(room_id)
            if name_lower in c.name.lower()
        ]
        if 1 <= ordinal <= len(matches):
            return matches[ordinal - 1]
        return None

    # ── Tick ──────────────────────────────────────────────────────────────

    async def tick(self, tick_count: int):
        await self._collect_planner_actions()
        if tick_count % 20 == 0:
            bubble_rooms = self._active_player_bubble()
            self._cull_outside_player_bubble(bubble_rooms)
        if tick_count % 50  == 0: await self._check_respawns(time.time())
        planner_interval = max(5, int(self._settings.get("planner_submit_interval_ticks") or 30))
        wander_interval = max(planner_interval, int(self._settings.get("wander_submit_interval_ticks") or 150))
        if self._planner_pool:
            if tick_count % planner_interval == 0:
                self._submit_planner_actions(time.time(), allow_wander=(tick_count % wander_interval == 0))
        else:
            if tick_count % planner_interval == 0:
                await self._creature_ai_tick(time.time())
            if tick_count % wander_interval == 0:
                await self._wander_tick()
        if tick_count % 80  == 0: await self._sniff_tick()
        self._maybe_log_perf()

    async def _check_respawns(self, now: float):
        bubble_rooms = self._active_player_bubble()
        for creature in [c for c in self._dead_creatures if now - c.death_time >= c.respawn_time]:
            self._dead_creatures.remove(creature)
            self.remove_creature(creature)
            valid = []
            for cfg in self._spawn_config:
                if cfg["template_id"] == creature.template_id:
                    valid = [r for r in cfg["rooms"]
                             if r in bubble_rooms
                             and not (self.server.world.get_room(r) and self.server.world.get_room(r).safe)]
                    break
            if not valid:
                if creature.current_room_id in self._hunting_rooms and creature.current_room_id in bubble_rooms:
                    valid = [creature.current_room_id]
                else:
                    continue
            room_id = random.choice(valid)
            new_c = self.spawn_creature(creature.template_id, room_id)
            if new_c:
                await self.server.world.broadcast_to_room(
                    room_id,
                    creature_arrival(new_c.full_name, "scurries in from the shadows")
                )
        await self._maintain_zone_populations(bubble_rooms)

    def _config_population_bump(self, cfg: dict) -> int:
        base = int(cfg.get("base_max_count", cfg.get("max_count", 1)) or 1)
        level = int(cfg.get("template_level", 1) or 1)
        if level <= self._zone_level_spawn_threshold:
            return 0
        return max(1, min(2, (base + 3) // 4))

    def _desired_population_for_config(self, cfg: dict) -> int:
        base = int(cfg.get("base_max_count", cfg.get("max_count", 1)) or 1)
        desired = base + self._config_population_bump(cfg)
        return max(1, desired)

    def _alive_creatures_for_config(self, cfg: dict) -> list[Creature]:
        room_ids = set(int(r) for r in (cfg.get("rooms") or []))
        template_id = cfg.get("template_id")
        return [
            creature for creature in self._creatures.values()
            if creature.alive
            and creature.template_id == template_id
            and int(getattr(creature, "current_room_id", 0) or 0) in room_ids
        ]

    async def _maintain_zone_populations(self, bubble_rooms: set[int] | None = None):
        bubble_rooms = set(bubble_rooms or set())
        if not bubble_rooms:
            return
        for cfg in self._spawn_config:
            desired = self._desired_population_for_config(cfg)
            alive = self._alive_creatures_for_config(cfg)
            deficit = desired - len(alive)
            if deficit <= 0:
                continue
            spawn_budget = min(deficit, 1)
            candidate_rooms = []
            for room_id in cfg.get("rooms") or []:
                if int(room_id or 0) not in bubble_rooms:
                    continue
                room = self.server.world.get_room(room_id)
                if not room or room.safe:
                    continue
                candidate_rooms.append(room_id)
            if not candidate_rooms:
                continue
            for _ in range(spawn_budget):
                room_id = random.choice(candidate_rooms)
                new_c = self.spawn_creature(cfg["template_id"], room_id)
                if not new_c:
                    continue
                await self.server.world.broadcast_to_room(
                    room_id,
                    creature_arrival(new_c.full_name, "emerges from deeper in the hunting grounds"),
                )

    def _player_bubble_distance(self) -> int:
        return max(1, int((self._settings or {}).get("active_player_bubble_rooms") or 60))

    def _active_player_bubble(self) -> set[int]:
        sessions = list(getattr(self.server, "sessions", None).playing())
        if not sessions:
            return set()
        max_distance = self._player_bubble_distance()
        visited: set[int] = set()
        queue = deque()
        for session in sessions:
            room = getattr(session, "current_room", None)
            room_id = int(getattr(room, "id", 0) or 0)
            if room_id <= 0 or room_id in visited:
                continue
            visited.add(room_id)
            queue.append((room_id, 0))
        while queue:
            room_id, dist = queue.popleft()
            if dist >= max_distance:
                continue
            room = self.server.world.get_room(room_id)
            if not room:
                continue
            for next_room_id in (room.exits or {}).values():
                next_room_id = int(next_room_id or 0)
                if next_room_id <= 0 or next_room_id in visited:
                    continue
                visited.add(next_room_id)
                queue.append((next_room_id, dist + 1))
        return visited

    def _cull_outside_player_bubble(self, bubble_rooms: set[int]):
        if not bubble_rooms:
            for creature in list(self._creatures.values()):
                if creature.alive:
                    ctx = dict(getattr(creature, "spawn_context", {}) or {})
                    if ctx.get("ignore_bubble_cull"):
                        continue
                    self.remove_creature(creature)
            return
        for creature in list(self._creatures.values()):
            room_id = int(getattr(creature, "current_room_id", 0) or 0)
            if not creature.alive:
                continue
            ctx = dict(getattr(creature, "spawn_context", {}) or {})
            if ctx.get("ignore_bubble_cull"):
                continue
            if room_id <= 0 or room_id not in bubble_rooms:
                self.remove_creature(creature)

    # Matches SyntheticPlayer._SYNTH_SESSION_OFFSET — used to give synthetic
    # players a stable planner ID that cannot collide with real session IDs.
    _SYNTH_SESSION_OFFSET: int = 1_000_000

    def _resolve_target_session(self, target_session_id: int):
        """Look up the target of a planner action by ID.

        Real player sessions have small positive IDs (1, 2, 3 …).
        Synthetic players use  synthetic_id + _SYNTH_SESSION_OFFSET  so they
        sit above the real-session range without collision.
        """
        sid = int(target_session_id or 0)
        if sid <= 0:
            return None
        if sid < self._SYNTH_SESSION_OFFSET:
            # Real player session
            return self.server.sessions.get_session(sid)
        # Synthetic player
        synth_id = sid - self._SYNTH_SESSION_OFFSET
        fake_mgr = getattr(self.server, "fake_players", None)
        if fake_mgr:
            return fake_mgr._actors.get(synth_id)
        return None

    def _submit_planner_actions(self, now: float, *, allow_wander: bool):
        if not self._planner_pool or self._planner_future is not None:
            return
        creatures = []
        for creature in list(self._creatures.values()):
            room = self.server.world.get_room(creature.current_room_id)
            exits = dict((room.exits or {})) if room else {}
            creatures.append({
                "id": int(creature.id),
                "room_id": int(creature.current_room_id or 0),
                "alive": bool(creature.alive),
                "aggressive": bool(creature.aggressive),
                "in_combat": bool(creature.in_combat),
                # getattr(target, "id", 0) works for both real sessions and
                # SyntheticPlayer (which now exposes .id = synthetic_id + offset)
                "target_session_id": int(getattr(getattr(creature, "target", None), "id", 0) or 0),
                "roundtime_end": float(getattr(creature, "roundtime_end", 0.0) or 0.0),
                "stunned_until": float(getattr(creature, "stunned_until", 0.0) or 0.0),
                "wander_chance": float(getattr(creature, "wander_chance", 0.0) or 0.0),
                "wander_rooms": [int(r) for r in (creature.wander_rooms or []) if int(r or 0) > 0],
                "can_wander": bool(creature.alive and not creature.in_combat),
                "exits": {str(k): int(v) for k, v in exits.items() if not str(k).startswith("go_") and int(v or 0) > 0},
            })

        # ── Real player sessions ─────────────────────────────────────────────
        players = []
        for session in self.server.sessions.playing():
            room = getattr(session, "current_room", None)
            players.append({
                "session_id": int(getattr(session, "id", 0) or 0),
                "room_id": int(getattr(room, "id", 0) or 0),
                "state": str(getattr(session, "state", "") or ""),
                "hidden": bool(getattr(session, "hidden", False)),
                "invisible": bool(has_effect(self.server, session, "invisible")),
                "is_dead": bool(getattr(session, "is_dead", False)),
                "is_synthetic": False,
            })

        # ── Synthetic players (fake population) ──────────────────────────────
        # Previously missing: the creature planner subprocess had no knowledge of
        # synthetic players so invasion creatures and aggressive mobs never picked
        # them as targets.  We include them here using their stable .id property
        # (synthetic_id + _SYNTH_SESSION_OFFSET) so the planner can treat them
        # identically to real players.
        fake_mgr = getattr(self.server, "fake_players", None)
        if fake_mgr:
            for actor in list(fake_mgr._actors.values()):
                actor_room = getattr(actor, "current_room", None)
                if not actor_room:
                    continue
                if not actor.connected or actor.state != "playing":
                    continue
                players.append({
                    "session_id": int(actor.id),   # synthetic_id + _SYNTH_SESSION_OFFSET
                    "room_id": int(getattr(actor_room, "id", 0) or 0),
                    "state": str(getattr(actor, "state", "") or ""),
                    "hidden": bool(getattr(actor, "hidden", False)),
                    "invisible": False,             # synthetic players are never invisible
                    "is_dead": bool(getattr(actor, "is_dead", False)),
                    "is_synthetic": True,
                })

        payload = {
            "now": float(now),
            "allow_wander": bool(allow_wander),
            "seed": random.randint(1, 2**31 - 1),
            "creatures": creatures,
            "players": players,
            "hunting_rooms": list(self._hunting_rooms),
        }
        self._planner_future = self._planner_pool.submit(plan_creature_actions, payload)
        self._perf["planner_submit"] += 1

    async def _collect_planner_actions(self):
        future = self._planner_future
        if not future or not future.done():
            return
        self._planner_future = None
        try:
            actions = list(future.result() or [])
        except Exception:
            log.exception("Creature planner failed")
            return
        self._perf["planner_done"] += 1
        for action in actions:
            kind = str(action.get("kind") or "")
            creature = self._creatures.get(int(action.get("creature_id") or 0))
            if not creature or not creature.alive:
                continue
            if kind == "clear_target":
                creature.in_combat = False
                creature.target = None
                continue
            if kind == "attack":
                session = self._resolve_target_session(int(action.get("target_session_id") or 0))
                if not session:
                    creature.in_combat = False
                    creature.target = None
                    continue
                creature.target = session
                creature.in_combat = True
                creature.choose_stance()
                if await attempt_special_action(self, creature, session, time.time()):
                    continue
                await self._creature_attack(creature, session)
                continue
            if kind == "engage":
                session = self._resolve_target_session(int(action.get("target_session_id") or 0))
                if not session:
                    continue
                creature.in_combat = True
                creature.target = session
                creature.choose_stance()
                attack = creature.choose_attack()
                target_name = getattr(session, "character_name", str(session))
                verb = (attack["verb_third"].replace("{target}", target_name)
                        if attack else f"attacks {target_name}")
                await self.server.world.broadcast_to_room(
                    creature.current_room_id,
                    colorize(creature.full_name.capitalize(), TextPresets.CREATURE_NAME) + " " + verb + "!"
                )
                continue
            if kind == "wander":
                await self._move_creature(
                    creature,
                    int(action.get("target_room_id") or 0),
                    str(action.get("direction") or "out"),
                )

    def _maybe_log_perf(self):
        interval = max(15.0, float(self._settings.get("perf_log_interval_seconds") or 60))
        now = time.time()
        if now - self._last_perf_log_at < interval:
            return
        self._last_perf_log_at = now
        log.info(
            "Creature perf: planner_submit=%d planner_done=%d alive=%d dead=%d",
            int(self._perf.get("planner_submit", 0)),
            int(self._perf.get("planner_done", 0)),
            int(self.alive_count),
            int(len(self._dead_creatures)),
        )

    async def _creature_ai_tick(self, now: float):
        for creature in list(self._creatures.values()):
            apply_passive_behavior(self, creature, now)
            recompute_group_modifiers(self, creature)
            if not creature.can_act():
                continue
            if creature.in_combat and creature.target:
                creature.choose_stance()
                target = creature.target
                if getattr(target, "is_dead", False):
                    creature.in_combat = False; creature.target = None; continue
                if (target.connected and target.state == "playing"
                        and target.current_room
                        and target.current_room.id == creature.current_room_id):
                    if target.hidden:
                        creature.in_combat = False; creature.target = None
                        await self.server.world.broadcast_to_room(
                            creature.current_room_id,
                            colorize(f"{creature.full_name.capitalize()} looks around, having lost sight of its target.",
                                     TextPresets.CREATURE_NAME))
                        continue
                    if await attempt_special_action(self, creature, target, now):
                        continue
                    await self._creature_attack(creature, target)
                else:
                    creature.in_combat = False; creature.target = None
                continue
            if creature.aggressive:
                creature.choose_stance()
                players = [p for p in self.server.world.get_players_in_room(creature.current_room_id)
                           if p.state == "playing"
                           and not p.hidden
                           and not has_effect(self.server, p, "invisible")
                           and not getattr(p, "is_dead", False)]
                if players:
                    target = random.choice(players)
                    creature.in_combat = True; creature.target = target
                    attack = creature.choose_attack()
                    verb = (attack["verb_third"].replace("{target}", target.character_name)
                            if attack else f"attacks {target.character_name}")
                    await self.server.world.broadcast_to_room(
                        creature.current_room_id,
                        colorize(creature.full_name.capitalize(), TextPresets.CREATURE_NAME) + " " + verb + "!"
                    )

    async def _creature_attack(self, creature: Creature, target):
        if hasattr(self.server, "combat"):
            await self.server.combat.creature_attacks_player(creature, target)

    async def _sniff_tick(self):
        for creature in list(self._creatures.values()):
            if not creature.alive or not creature.aggressive:
                continue
            hidden = [p for p in self.server.world.get_players_in_room(creature.current_room_id)
                      if p.state == "playing" and p.hidden and not has_effect(self.server, p, "invisible")]
            if not hidden:
                continue
            perception = creature.level * 3 + sniff_bonus(creature) + random.randint(1, 50)
            for target in hidden:
                stalking = target.skills.get("stalking_hiding", {}).get("bonus", 0) or \
                           ((getattr(target, "stat_dexterity", 50) - 50) // 3 + target.level * 2)
                if perception > stalking + random.randint(1, 50):
                    target.hidden = False
                    msgs = [
                        f"{creature.full_name.capitalize()} sniffs the air and turns toward {target.character_name}!",
                        f"{creature.full_name.capitalize()} snarls and lunges toward {target.character_name}'s hiding spot!",
                        f"{creature.full_name.capitalize()} suddenly focuses on where {target.character_name} is concealed!",
                    ]
                    await self.server.world.broadcast_to_room(creature.current_room_id,
                                                              colorize(random.choice(msgs), TextPresets.CREATURE_NAME))
                    await target.send_line(colorize(
                        f"{creature.full_name.capitalize()} has detected you!  You are no longer hidden.",
                        TextPresets.WARNING))
                    creature.in_combat = True; creature.target = target
                elif random.random() < 0.4:
                    await self.server.world.broadcast_to_room(
                        creature.current_room_id,
                        colorize(random.choice([
                            f"{creature.full_name.capitalize()} sniffs the air suspiciously.",
                            f"{creature.full_name.capitalize()} growls softly and glances around.",
                            f"{creature.full_name.capitalize()} seems unsettled, as if sensing a presence.",
                        ]), TextPresets.CREATURE_NAME))

    async def _wander_tick(self):
        for creature in list(self._creatures.values()):
            if not creature.alive or creature.in_combat:
                continue
            if random.random() > creature.wander_chance:
                continue
            room = self.server.world.get_room(creature.current_room_id)
            if not room or not room.exits:
                continue
            cardinal = {d: r for d, r in room.exits.items() if not d.startswith("go_")}
            if not cardinal:
                continue
            direction = random.choice(list(cardinal.keys()))
            target_room_id = cardinal[direction]
            target_room = self.server.world.get_room(target_room_id)
            if not target_room or target_room.safe:
                continue
            if creature.wander_rooms and target_room_id not in creature.wander_rooms:
                continue
            if target_room_id not in self._hunting_rooms:
                continue
            await self._move_creature(creature, target_room_id, direction)
            for follower in pack_follow_candidates(self, creature):
                if random.random() > 0.70:
                    continue
                if follower.wander_rooms and target_room_id not in follower.wander_rooms:
                    continue
                await self._move_creature(follower, target_room_id, direction, group_follow=True)

    @property
    def creature_count(self):
        return len(self._creatures)

    async def _move_creature(self, creature: Creature, target_room_id: int, direction: str | None = None, *, group_follow=False):
        old = creature.current_room_id
        direction = direction or self.server.world.get_direction_between(old, target_room_id) or "out"
        try:
            self._room_creatures.get(old, []).remove(creature.id)
        except ValueError:
            pass
        tracker = getattr(self.server, "tracking", None)
        if tracker:
            try:
                tracker.record_departure(
                    actor_kind="creature",
                    actor_id=int(getattr(creature, "id", 0) or 0),
                    actor_name=getattr(creature, "name", "") or "creature",
                    from_room_id=int(old),
                    to_room_id=int(target_room_id),
                    direction=str(direction or "out"),
                    actor_level=int(getattr(creature, "level", 1) or 1),
                )
            except Exception as e:
                log.debug("Failed to record creature trail: %s", e)

        creature.current_room_id = target_room_id
        self._room_creatures.setdefault(target_room_id, []).append(creature.id)
        await self.server.world.broadcast_to_room(
            old,
            creature_departure(creature.full_name.capitalize(), direction),
        )
        await self.server.world.broadcast_to_room(
            target_room_id,
            creature_arrival(creature.full_name.capitalize(), "pads in close behind its pack" if group_follow else "just arrived"),
        )

    @property
    def alive_count(self):
        return sum(1 for c in self._creatures.values() if c.alive)
