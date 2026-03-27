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
import random
import re
import time
import logging
from typing import Dict, List, Optional

from server.core.entity.creature.creature import Creature
from server.core.entity.creature.creature_data import get_template, get_all_templates, register_templates
from server.core.entity.creature.lua_mob_loader import load_all_mob_luas
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

    # ── Initialization ────────────────────────────────────────────────────

    async def initialize(self):
        scripts_path = self.server.config.get("paths.scripts", "./scripts")

        # ── Phase 1: Lua mob files (authoritative for scripted creatures) ──
        lua_templates = load_all_mob_luas(scripts_path)
        lua_registered = register_templates(lua_templates)
        log.info("CreatureManager: registered %d Lua mob templates", lua_registered)

        # ── Phase 2: SQL creatures + spawn_points (additive, never cancels Lua) ──
        sql_configs = self._load_sql_spawn_configs()

        # ── Phase 3: Build unified spawn configs from ALL sources ──────────
        self._build_spawn_configs(lua_templates, sql_configs)

        # ── Phase 4: Initial spawn ────────────────────────────────────────
        spawned = 0
        for config in self._spawn_config:
            template = get_template(config["template_id"])
            if not template or not config["rooms"]:
                continue
            for _ in range(config["max_count"]):
                room_id = random.choice(config["rooms"])
                if self.spawn_creature(config["template_id"], room_id):
                    spawned += 1

        log.info(
            "CreatureManager initialized: %d creatures spawned, %d configs "
            "(%d Lua, %d SQL), %d hunting rooms",
            spawned, len(self._spawn_config),
            self._lua_config_count, self._sql_config_count,
            len(self._hunting_rooms)
        )

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

    def _build_spawn_configs(self, lua_templates: dict, sql_configs: list = None):
        world = self.server.world
        configs = []
        hunting = set()

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
                if isinstance(r, int) and world.get_room(r) and not world.get_room(r).safe
            ]
            valid_wander = [
                r for r in wander_rooms
                if isinstance(r, int) and world.get_room(r) and not world.get_room(r).safe
            ]
            if not valid_spawn:
                continue

            configs.append({
                "template_id": tid,
                "max_count":   max_count,
                "rooms":       valid_spawn,
                "wander":      valid_wander,
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
                    "rooms":       valid_spawn,
                    "wander":      valid_spawn,
                    "source":      "sql",
                })
                hunting.update(valid_spawn)
                sql_count += 1

        self._spawn_config = configs
        self._hunting_rooms = hunting
        self._lua_config_count = lua_count
        self._sql_config_count = sql_count
        self._legacy_config_count = 0

    # ── Spawn helpers ─────────────────────────────────────────────────────

    def spawn_creature(self, template_id: str, room_id: int) -> Optional[Creature]:
        room = self.server.world.get_room(room_id)
        if room and room.safe:
            log.warning("Blocked creature spawn in safe room %d", room_id)
            return None
        template = get_template(template_id)
        if not template:
            log.warning("Unknown creature template: %s", template_id)
            return None
        creature = Creature(template)
        creature.current_room_id = room_id
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
        if tick_count % 50  == 0: await self._check_respawns(time.time())
        if tick_count % 30  == 0: await self._creature_ai_tick(time.time())
        if tick_count % 150 == 0: await self._wander_tick()
        if tick_count % 80  == 0: await self._sniff_tick()

    async def _check_respawns(self, now: float):
        for creature in [c for c in self._dead_creatures if now - c.death_time >= c.respawn_time]:
            self._dead_creatures.remove(creature)
            self.remove_creature(creature)
            valid = []
            for cfg in self._spawn_config:
                if cfg["template_id"] == creature.template_id:
                    valid = [r for r in cfg["rooms"]
                             if not (self.server.world.get_room(r) and self.server.world.get_room(r).safe)]
                    break
            if not valid:
                if creature.current_room_id in self._hunting_rooms:
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

    async def _creature_ai_tick(self, now: float):
        for creature in list(self._creatures.values()):
            if not creature.can_act():
                continue
            if creature.in_combat and creature.target:
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
                    await self._creature_attack(creature, target)
                else:
                    creature.in_combat = False; creature.target = None
                continue
            if creature.aggressive:
                players = [p for p in self.server.world.get_players_in_room(creature.current_room_id)
                           if p.state == "playing" and not p.hidden and not getattr(p, "is_dead", False)]
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
                      if p.state == "playing" and p.hidden]
            if not hidden:
                continue
            perception = creature.level * 3 + random.randint(1, 50)
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
            old = creature.current_room_id
            try:
                self._room_creatures.get(old, []).remove(creature.id)
            except ValueError:
                pass
            creature.current_room_id = target_room_id
            self._room_creatures.setdefault(target_room_id, []).append(creature.id)
            await self.server.world.broadcast_to_room(old,
                creature_departure(creature.full_name.capitalize(), direction))
            await self.server.world.broadcast_to_room(target_room_id,
                creature_arrival(creature.full_name.capitalize(), "just arrived"))

    @property
    def creature_count(self):
        return len(self._creatures)

    @property
    def alive_count(self):
        return sum(1 for c in self._creatures.values() if c.alive)
