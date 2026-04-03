"""
TownTroubleManager
------------------
Lua-authored dynamic city incidents for Ta'Vaalor.
"""

from __future__ import annotations

import copy
import json
import logging
import random
import time
from datetime import datetime

from server.core.commands.player.info import award_fame
from server.core.commands.player.inventory import auto_stow_item
from server.core.engine.treasure import generate_box
from server.core.entity.creature.creature_data import CREATURE_TEMPLATES, get_template
from server.core.protocol.colors import TextPresets, colorize

log = logging.getLogger(__name__)


def _json_dumps(value) -> str:
    try:
        return json.dumps(value or {}, separators=(",", ":"))
    except Exception:
        return "{}"


def _json_loads(value, default=None):
    if default is None:
        default = {}
    if value in (None, "", b""):
        return copy.deepcopy(default)
    if isinstance(value, (dict, list)):
        return copy.deepcopy(value)
    try:
        parsed = json.loads(value)
        return parsed if parsed is not None else copy.deepcopy(default)
    except Exception:
        return copy.deepcopy(default)


def _dt_to_ts(value) -> float:
    if not value:
        return 0.0
    if isinstance(value, datetime):
        return value.timestamp()
    try:
        return float(value)
    except Exception:
        return 0.0


class TownTroubleManager:
    def __init__(self, server):
        self.server = server
        self._defs = {}
        self._config = {}
        self._cities = {}
        self._districts = {}
        self._variants = {}
        self._incidents = {}
        self._active: dict[int, dict] = {}
        self._last_roll_at = 0.0
        self._last_resync_at = 0.0
        self._city_cooldowns: dict[str, float] = {}
        self._boot_login_started = False

    def _write_async(self, sql: str, params) -> bool:
        writer = getattr(self.server, "persistence_writer", None)
        if writer and writer.enabled:
            return bool(writer.submit(sql, params))
        return False

    async def initialize(self):
        self._defs = getattr(self.server.lua, "get_town_trouble", lambda: {})() or {}
        self._config = dict(self._defs.get("config") or {})
        self._cities = dict(self._defs.get("cities") or {})
        self._districts = dict(self._defs.get("districts") or {})
        self._variants = dict(self._defs.get("hostile_variants") or {})
        self._incidents = dict(self._defs.get("incidents") or {})
        self._validate_definitions()
        self._last_roll_at = time.time()
        self._load_active_from_db()
        for actor in list(self._active.values()):
            if actor.get("state") == "active" and not actor.get("active_creature_ids"):
                await self._spawn_current_stage(actor)
        log.info(
            "TownTroubleManager ready (%d cities, %d districts, %d variants, %d incidents, %d active)",
            len(self._cities),
            len(self._districts),
            len(self._variants),
            len(self._incidents),
            len(self._active),
        )

    async def tick(self, tick_count: int):
        if not self._incidents:
            return
        now = time.time()
        if tick_count % 20 == 0:
            await self._tick_active(now)
        if tick_count % 30 == 0:
            await self._maybe_start_incident(now)

    async def on_player_login(self, session):
        if not getattr(session, "character_id", None):
            return
        await self._grant_pending_rewards(session)
        room = getattr(session, "current_room", None)
        if not room:
            return
        await self._maybe_force_boot_incident(session)
        incident = self._incident_for_room(int(getattr(room, "id", 0) or 0))
        if not incident:
            return
        label = incident.get("district_label") or "the district"
        phase = str(incident.get("state") or "active").strip().lower()
        line = (
            f"  Trouble is building in {label}.  Watch the crier and be ready when the ward breaks."
            if phase == "prelude"
            else f"  Trouble is active in {label}.  Watch for the crier's call and keep steel ready."
        )
        await session.send_line(colorize(
            line,
            TextPresets.WARNING,
        ))

    def get_room_lines(self, room_id: int, session=None) -> list[str]:
        incident = self._incident_for_room(room_id)
        if not incident:
            return []
        lines = []
        for text in incident.get("scene_lines") or []:
            lines.append(colorize(text, TextPresets.WARNING))
        for text in incident.get("room_lines") or []:
            lines.append(colorize(text, TextPresets.WARNING))
        return lines

    def record_damage(self, attacker, creature, amount: int):
        if int(amount or 0) <= 0 or getattr(attacker, "is_synthetic_player", False):
            return
        ctx = dict(getattr(creature, "spawn_context", {}) or {})
        incident_id = int(ctx.get("town_trouble_id") or 0)
        if incident_id <= 0 or incident_id not in self._active:
            return
        character_id = int(getattr(attacker, "character_id", 0) or 0)
        if character_id <= 0:
            return
        self._upsert_participation(incident_id, character_id, damage=int(amount or 0), kills=0)

    async def record_kill(self, attacker, creature):
        ctx = dict(getattr(creature, "spawn_context", {}) or {})
        incident_id = int(ctx.get("town_trouble_id") or 0)
        if incident_id <= 0 or incident_id not in self._active:
            return
        actor = self._active[incident_id]
        active_ids = [int(cid) for cid in (actor.get("active_creature_ids") or []) if int(cid or 0) > 0]
        actor["active_creature_ids"] = [cid for cid in active_ids if cid != int(getattr(creature, "id", 0) or 0)]
        self._save_incident_state(actor)
        self._credit_room_witnesses(creature)
        if not getattr(attacker, "is_synthetic_player", False):
            character_id = int(getattr(attacker, "character_id", 0) or 0)
            room_id = int(getattr(creature, "current_room_id", 0) or 0)
            if character_id > 0 and room_id > 0:
                in_room = any(
                    int(getattr(session, "character_id", 0) or 0) == character_id
                    for session in self.server.world.get_players_in_room(room_id)
                    if not getattr(session, "is_synthetic_player", False)
                )
                if not in_room:
                    self._upsert_participation(incident_id, character_id, damage=0, kills=1)

    async def _tick_active(self, now: float):
        resync_seconds = max(20, int(self._config.get("resync_active_hostiles_seconds") or 60))
        if now - self._last_resync_at >= resync_seconds:
            self._last_resync_at = now
            self._resync_active_creatures()

        for actor in list(self._active.values()):
            phase = str(actor.get("state") or "").strip().lower()
            if phase == "prelude":
                changed = False
                if self._emit_due_prelude_warnings(actor, now):
                    changed = True
                if self._should_enable_music_override(actor, now) and not actor.get("music_override_started"):
                    actor["music_override_started"] = True
                    changed = True
                    await self._push_sync_for_city(int(actor.get("city_zone_id") or 0))
                if now >= float(actor.get("starts_at_ts") or 0.0):
                    actor["state"] = "active"
                    actor["music_override_started"] = True
                    actor["next_announce_at_ts"] = now + max(90, int(self._config.get("periodic_announcement_seconds") or 180))
                    self._save_incident_state(actor)
                    await self._broadcast_incident(actor, "crier_open")
                    await self._spawn_current_stage(actor)
                    await self._push_sync_for_city(int(actor.get("city_zone_id") or 0))
                    continue
                if changed:
                    self._save_incident_state(actor)
                continue
            if phase != "active":
                continue
            if now >= float(actor.get("expires_at_ts") or 0.0):
                await self._resolve_incident(actor, success=False)
                continue
            if now >= float(actor.get("next_announce_at_ts") or 0.0):
                await self._broadcast_incident(actor, "crier_progress")
                actor["next_announce_at_ts"] = now + max(90, int(self._config.get("periodic_announcement_seconds") or 180))
                self._save_incident_state(actor)
            if not self._stage_has_living_hostiles(actor):
                await self._advance_incident(actor)

    async def _maybe_start_incident(self, now: float):
        if len(self._active) >= max(1, int(self._config.get("max_active_incidents") or 1)):
            return
        min_players = max(1, int(self._config.get("min_players_online") or 1))
        sessions = [s for s in self.server.sessions.playing() if getattr(s, "current_room", None)]
        if len(sessions) < min_players:
            return
        interval = max(60, int(self._config.get("incident_roll_interval_seconds") or 360))
        if now - self._last_roll_at < interval:
            return
        self._last_roll_at = now

        for city_key, city in self._cities.items():
            zone_id = int(city.get("zone_id") or 0)
            if zone_id <= 0:
                continue
            city_players = [s for s in sessions if int(getattr(getattr(s, "current_room", None), "zone_id", 0) or 0) == zone_id]
            if len(city_players) < min_players:
                continue
            if any(str(row.get("city_key") or "") == city_key for row in self._active.values()):
                continue
            if now < float(self._city_cooldowns.get(city_key, 0.0) or 0.0):
                continue
            await self._start_incident(city_key, city, now)
            return

    async def _start_incident(self, city_key: str, city: dict, now: float):
        choices = []
        for incident in self._incidents.values():
            if str(incident.get("city_key") or "") != city_key:
                continue
            weight = max(1, int(incident.get("weight") or 1))
            choices.extend([incident] * weight)
        if not choices:
            return
        chosen = dict(random.choice(choices))
        district_ids = [did for did in (chosen.get("district_ids") or []) if did in self._districts]
        district_label = self._district_label(district_ids)
        duration = random.randint(
            max(120, int(chosen.get("min_duration_seconds") or 600)),
            max(120, int(chosen.get("max_duration_seconds") or 900)),
        )
        prelude_duration = self._prelude_duration_seconds()
        target_level = self._target_level()
        starts_at_ts = now + prelude_duration
        next_announce = starts_at_ts + max(90, int(self._config.get("periodic_announcement_seconds") or 180))
        initial_phase = "prelude" if prelude_duration > 0 else "active"
        actor = {
            "id": self._insert_incident_row(
                city_key=city_key,
                incident_key=str(chosen.get("key") or ""),
                district_key=district_ids[0] if district_ids else "",
                difficulty=max(1, int(chosen.get("difficulty") or 1)),
                target_level=target_level,
                duration_seconds=duration,
                stage_index=0,
                next_announce_ts=next_announce,
                expires_at_ts=starts_at_ts + duration,
                state_json={
                    "phase": initial_phase,
                    "starts_at_ts": starts_at_ts,
                    "music_override_started": False,
                    "warning_offsets_sent": [],
                    "active_creature_ids": [],
                },
            ),
            "city_key": city_key,
            "city_zone_id": int(city.get("zone_id") or 0),
            "incident_key": str(chosen.get("key") or ""),
            "district_key": district_ids[0] if district_ids else "",
            "district_ids": district_ids,
            "district_label": district_label,
            "difficulty": max(1, int(chosen.get("difficulty") or 1)),
            "duration_seconds": duration,
            "target_level": target_level,
            "stage_index": 0,
            "active_creature_ids": [],
            "starts_at_ts": starts_at_ts,
            "music_override_started": False,
            "warning_offsets_sent": [],
            "expires_at_ts": starts_at_ts + duration,
            "next_announce_at_ts": next_announce,
            "state": initial_phase,
            "scene_lines": self._collect_scene_lines(district_ids),
            "room_lines": list(chosen.get("room_lines") or []),
            "covered_room_ids": self._collect_district_rooms(district_ids),
        }
        if int(actor["id"] or 0) <= 0:
            return
        self._active[int(actor["id"])] = actor
        self._save_incident_state(actor)
        if initial_phase == "prelude":
            if self._emit_due_prelude_warnings(actor, now):
                self._save_incident_state(actor)
        else:
            await self._broadcast_incident(actor, "crier_open")
            await self._spawn_current_stage(actor)
            await self._push_sync_for_city(int(actor.get("city_zone_id") or 0))

    async def _advance_incident(self, actor: dict):
        incident_def = self._incident_def(actor)
        stages = list(incident_def.get("stages") or [])
        current_index = int(actor.get("stage_index") or 0)
        if current_index < len(stages):
            completion_line = str((stages[current_index] or {}).get("completion_announcement") or "").strip()
            if completion_line:
                await self._broadcast_city(
                    int(actor.get("city_zone_id") or 0),
                    self._format_line(actor, completion_line),
                    preset=TextPresets.WARNING,
                )
        actor["stage_index"] = current_index + 1
        actor["active_creature_ids"] = []
        self._save_incident_state(actor)
        if actor["stage_index"] >= len(stages):
            await self._resolve_incident(actor, success=True)
            return
        await self._spawn_current_stage(actor)

    async def _spawn_current_stage(self, actor: dict):
        incident_def = self._incident_def(actor)
        stages = list(incident_def.get("stages") or [])
        stage_index = int(actor.get("stage_index") or 0)
        if stage_index < 0 or stage_index >= len(stages):
            return
        stage = dict(stages[stage_index] or {})
        stage_room_ids = [int(rid) for rid in (stage.get("spawn_room_ids") or []) if int(rid or 0) > 0]
        live_ids = []
        for hostile_cfg in stage.get("hostiles") or []:
            variant_id = str(hostile_cfg.get("variant_id") or "").strip().lower()
            count = max(1, int(hostile_cfg.get("count") or 1))
            for _ in range(count):
                room_id = random.choice(stage_room_ids) if stage_room_ids else 0
                creature = self._spawn_variant(actor, variant_id, room_id)
                if creature:
                    live_ids.append(int(creature.id))
        actor["active_creature_ids"] = live_ids
        self._save_incident_state(actor)

    async def _resolve_incident(self, actor: dict, *, success: bool):
        incident_id = int(actor.get("id") or 0)
        if incident_id <= 0:
            return
        actor["state"] = "resolved" if success else "failed"
        self._save_resolved_state(actor, success=success)
        await self._broadcast_incident(actor, "crier_success" if success else "crier_fail")
        if success:
            self._queue_rewards(actor)
            for session in list(self.server.sessions.playing()):
                if getattr(session, "character_id", None):
                    await self._grant_pending_rewards(session, incident_id=incident_id)
        cooldown = max(0, int(self._config.get("incident_cooldown_seconds") or 0))
        self._city_cooldowns[str(actor.get("city_key") or "")] = time.time() + cooldown
        self._active.pop(incident_id, None)
        await self._push_sync_for_city(int(actor.get("city_zone_id") or 0))

    def _spawn_variant(self, actor: dict, variant_id: str, room_id: int):
        if room_id <= 0:
            return None
        variant = dict(self._variants.get(variant_id) or {})
        base_template_id = str(variant.get("base_template_id") or "").strip()
        base = copy.deepcopy(get_template(base_template_id) or {})
        if not base:
            log.warning("TownTroubleManager: missing base template '%s' for variant '%s'", base_template_id, variant_id)
            return None
        target_level = max(1, int(actor.get("target_level") or 1) + int(variant.get("level_offset") or 0))
        template_id = f"town_trouble_{actor['id']}_{variant_id}_{target_level}"
        CREATURE_TEMPLATES[template_id] = self._scaled_template(template_id, base, variant, target_level)
        spawn_context = {
            "special_spawn": True,
            "allow_safe_room": True,
            "ignore_bubble_cull": True,
            "town_trouble_id": int(actor.get("id") or 0),
            "town_trouble_hostile": True,
            "town_trouble_variant": variant_id,
            "town_trouble_base_template": base_template_id,
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

    def _scaled_template(self, template_id: str, base: dict, variant: dict, target_level: int) -> dict:
        base_level = max(1, int(base.get("level", 1) or 1))
        level_scale = max(0.45, float(target_level) / float(base_level))
        hp_mult = max(0.10, float(variant.get("hp_mult") or 1.0))
        as_mult = max(0.10, float(variant.get("as_mult") or 1.0))
        ds_mult = max(0.10, float(variant.get("ds_mult") or 1.0))
        td_mult = max(0.10, float(variant.get("td_mult") or 1.0))

        tmpl = copy.deepcopy(base)
        tmpl["template_id"] = template_id
        tmpl["name"] = str(variant.get("name") or base.get("name") or "troublemaker")
        tmpl["article"] = str(variant.get("article") or base.get("article") or "a")
        tmpl["description"] = str(variant.get("description") or base.get("description") or "")
        tmpl["level"] = max(1, int(target_level))
        tmpl["hp"] = max(18, int((int(base.get("hp", 30) or 30) * level_scale * hp_mult)))
        tmpl["as_melee"] = max(20, int((int(base.get("as_melee", 35) or 35) * level_scale * as_mult)))
        tmpl["ds_melee"] = max(10, int((int(base.get("ds_melee", 20) or 20) * level_scale * ds_mult)))
        tmpl["ds_ranged"] = max(10, int((int(base.get("ds_ranged", tmpl["ds_melee"]) or tmpl["ds_melee"]) * level_scale * ds_mult)))
        tmpl["ds_bolt"] = max(10, int((int(base.get("ds_bolt", tmpl["ds_melee"]) or tmpl["ds_melee"]) * level_scale * ds_mult)))
        base_td = int(base.get("td", base.get("level", 1) * 3) or (base.get("level", 1) * 3))
        tmpl["td"] = max(5, int(base_td * level_scale * td_mult))
        tmpl["td_spiritual"] = max(5, int(int(base.get("td_spiritual", tmpl["td"]) or tmpl["td"]) * level_scale * td_mult))
        tmpl["td_elemental"] = max(5, int(int(base.get("td_elemental", tmpl["td"]) or tmpl["td"]) * level_scale * td_mult))
        tmpl["treasure"] = dict(variant.get("treasure") or {"coins": False, "gems": False, "magic": False, "boxes": False})
        attacks = []
        for attack in list(base.get("attacks") or []):
            row = dict(attack or {})
            row["as"] = max(20, int((int(row.get("as", tmpl["as_melee"]) or tmpl["as_melee"]) * level_scale * as_mult)))
            attacks.append(row)
        if attacks:
            tmpl["attacks"] = attacks
        return tmpl

    def _target_level(self) -> int:
        levels = [int(getattr(session, "level", 1) or 1) for session in self.server.sessions.playing()]
        average = round(sum(levels) / len(levels)) if levels else 1
        floor = max(1, int(self._config.get("average_level_floor") or 1))
        ceiling = max(floor, int(self._config.get("average_level_ceiling") or floor))
        return max(floor, min(ceiling, int(average)))

    def _incident_def(self, actor: dict) -> dict:
        return dict(self._incidents.get(str(actor.get("incident_key") or "")) or {})

    def _district_label(self, district_ids: list[str]) -> str:
        labels = []
        for district_id in district_ids:
            district = dict(self._districts.get(district_id) or {})
            label = str(district.get("label") or "").strip()
            if label:
                labels.append(label)
        if not labels:
            return "the district"
        if len(labels) == 1:
            return labels[0]
        if len(labels) == 2:
            return f"{labels[0]} and {labels[1]}"
        return ", ".join(labels[:-1]) + f", and {labels[-1]}"

    def _collect_district_rooms(self, district_ids: list[str]) -> list[int]:
        room_ids = []
        seen = set()
        for district_id in district_ids:
            district = dict(self._districts.get(district_id) or {})
            for room_id in district.get("room_ids") or []:
                room_id = int(room_id or 0)
                if room_id > 0 and room_id not in seen:
                    seen.add(room_id)
                    room_ids.append(room_id)
        return room_ids

    def _collect_scene_lines(self, district_ids: list[str]) -> list[str]:
        lines = []
        seen = set()
        for district_id in district_ids:
            district = dict(self._districts.get(district_id) or {})
            for text in district.get("scene_lines") or []:
                text = str(text or "").strip()
                if text and text not in seen:
                    seen.add(text)
                    lines.append(text)
        return lines

    async def _broadcast_incident(self, actor: dict, key: str):
        incident_def = self._incident_def(actor)
        lines = list(incident_def.get(key) or [])
        if not lines:
            return
        line = self._format_line(actor, random.choice(lines), key=key)
        await self._broadcast_city(int(actor.get("city_zone_id") or 0), line, preset=TextPresets.WARNING)

    def _format_line(self, actor: dict, text: str, *, key: str = "", replacements: dict | None = None) -> str:
        room_refs = self._announcement_room_refs(actor)
        line = str(text or "").replace("%district%", str(actor.get("district_label") or "the district"))
        line = line.replace("%room_refs%", room_refs)
        for src, dst in (replacements or {}).items():
            line = line.replace(str(src), str(dst))
        if key in {"crier_open", "crier_progress"} and room_refs and "%room_refs%" not in str(text or ""):
            line = f"{line.rstrip()}  {room_refs}"
        return line

    async def _broadcast_city(self, zone_id: int, text: str, *, preset=None):
        if not text:
            return
        payload = colorize(text, preset or TextPresets.SYSTEM)
        for session in self.server.sessions.playing():
            room = getattr(session, "current_room", None)
            if not room:
                continue
            if int(getattr(room, "zone_id", 0) or 0) != int(zone_id or 0):
                continue
            await session.send_line(payload)

    def _incident_for_room(self, room_id: int) -> dict | None:
        room_id = int(room_id or 0)
        for actor in self._active.values():
            if room_id in set(actor.get("covered_room_ids") or []):
                return actor
        return None

    def get_audio_zone_override(self, room_id: int) -> str | None:
        room_id = int(room_id or 0)
        room = self.server.world.get_room(room_id) if room_id > 0 else None
        zone_id = int(getattr(room, "zone_id", 0) or 0)
        if zone_id <= 0:
            return None
        now = time.time()
        for actor in self._active.values():
            if int(actor.get("city_zone_id") or 0) != zone_id:
                continue
            phase = str(actor.get("state") or "").strip().lower()
            if phase == "prelude" and not self._should_enable_music_override(actor, now):
                continue
            if phase not in {"prelude", "active"}:
                continue
            incident_def = self._incident_def(actor)
            override = str(incident_def.get("audio_zone_override") or self._config.get("default_audio_zone_override") or "").strip()
            if override:
                return override
        return None

    def _active_stage_room_ids(self, actor: dict) -> list[int]:
        incident_def = self._incident_def(actor)
        stages = list(incident_def.get("stages") or [])
        stage_index = int(actor.get("stage_index") or 0)
        if stage_index < 0 or stage_index >= len(stages):
            return []
        stage = dict(stages[stage_index] or {})
        return [int(rid) for rid in (stage.get("spawn_room_ids") or []) if int(rid or 0) > 0]

    def get_active_response_targets(self, zone_id: int | None = None) -> list[dict]:
        requested_zone = int(zone_id or 0)
        targets = []
        for actor in sorted(self._active.values(), key=lambda row: int(row.get("id") or 0)):
            actor_zone = int(actor.get("city_zone_id") or 0)
            if requested_zone > 0 and actor_zone != requested_zone:
                continue
            if str(actor.get("state") or "").strip().lower() != "active":
                continue
            room_ids = []
            creatures = getattr(self.server, "creatures", None)
            if creatures:
                seen = set()
                for creature_id in actor.get("active_creature_ids") or []:
                    creature = creatures.get_creature(int(creature_id or 0))
                    room_id = int(getattr(creature, "current_room_id", 0) or 0) if creature and getattr(creature, "alive", False) else 0
                    if room_id > 0 and room_id not in seen:
                        seen.add(room_id)
                        room_ids.append(room_id)
            if not room_ids:
                room_ids = self._active_stage_room_ids(actor)
            if not room_ids:
                continue
            targets.append(
                {
                    "incident_id": int(actor.get("id") or 0),
                    "incident_key": str(actor.get("incident_key") or ""),
                    "city_key": str(actor.get("city_key") or ""),
                    "city_zone_id": actor_zone,
                    "target_level": int(actor.get("target_level") or 1),
                    "room_ids": room_ids,
                    "district_ids": [str(v) for v in (actor.get("district_ids") or []) if str(v or "").strip()],
                }
            )
        return targets

    def _announcement_room_refs(self, actor: dict) -> str:
        incident_def = self._incident_def(actor)
        stages = list(incident_def.get("stages") or [])
        stage_index = max(0, int(actor.get("stage_index") or 0))
        if stage_index >= len(stages):
            return ""
        stage = dict(stages[stage_index] or {})
        room_ids = [int(rid) for rid in (stage.get("spawn_room_ids") or []) if int(rid or 0) > 0]
        if not room_ids:
            return ""
        hint_count = max(1, int(self._config.get("announcement_room_hint_count") or 2))
        room_ids = room_ids[:hint_count]
        if len(room_ids) == 1:
            return f"Reports point toward room #{room_ids[0]}."
        refs = " and ".join(f"#{rid}" for rid in room_ids)
        return f"Reports point toward rooms {refs}."

    def _credit_room_witnesses(self, creature):
        room_id = int(getattr(creature, "current_room_id", 0) or 0)
        if room_id <= 0:
            return
        ctx = dict(getattr(creature, "spawn_context", {}) or {})
        incident_id = int(ctx.get("town_trouble_id") or 0)
        if incident_id <= 0 or incident_id not in self._active:
            return
        threshold_damage = max(1, int(self._config.get("min_participation_damage") or 1))
        for session in self.server.world.get_players_in_room(room_id):
            if getattr(session, "is_synthetic_player", False):
                continue
            character_id = int(getattr(session, "character_id", 0) or 0)
            if character_id <= 0:
                continue
            self._upsert_participation(incident_id, character_id, damage=threshold_damage, kills=0)

    def _stage_has_living_hostiles(self, actor: dict) -> bool:
        live = []
        for creature_id in list(actor.get("active_creature_ids") or []):
            creature = self.server.creatures.get_creature(int(creature_id or 0))
            if creature and getattr(creature, "alive", False):
                live.append(int(creature.id))
        actor["active_creature_ids"] = live
        return bool(live)

    def _resync_active_creatures(self):
        for actor in self._active.values():
            actor["active_creature_ids"] = [
                int(creature_id)
                for creature_id in (actor.get("active_creature_ids") or [])
                if self.server.creatures.get_creature(int(creature_id or 0))
            ]
            self._save_incident_state(actor)

    def _load_active_from_db(self):
        db = getattr(self.server, "db", None)
        if not db or not db._pool:
            return
        conn = db._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, city_key, incident_key, district_key, state, target_level,
                       difficulty, duration_seconds, stage_index, state_json,
                       started_at, expires_at, next_announce_at
                FROM town_trouble_incidents
                WHERE state = 'active' AND expires_at > NOW()
                ORDER BY id
                """
            )
            rows = cur.fetchall() or []
        except Exception as exc:
            log.error("TownTroubleManager: failed loading active incidents (%s)", exc, exc_info=True)
            return
        finally:
            conn.close()

        for row in rows:
            incident_key = str(row.get("incident_key") or "")
            incident_def = dict(self._incidents.get(incident_key) or {})
            if not incident_def:
                continue
            district_ids = [did for did in (incident_def.get("district_ids") or []) if did in self._districts]
            city_key = str(row.get("city_key") or "")
            city = dict(self._cities.get(city_key) or {})
            state_data = _json_loads(row.get("state_json"), default={})
            actor = {
                "id": int(row.get("id") or 0),
                "city_key": city_key,
                "city_zone_id": int(city.get("zone_id") or 0),
                "incident_key": incident_key,
                "district_key": str(row.get("district_key") or ""),
                "district_ids": district_ids,
                "district_label": self._district_label(district_ids),
                "difficulty": max(1, int(row.get("difficulty") or incident_def.get("difficulty") or 1)),
                "duration_seconds": max(120, int(row.get("duration_seconds") or incident_def.get("max_duration_seconds") or 600)),
                "target_level": max(1, int(row.get("target_level") or 1)),
                "stage_index": max(0, int(row.get("stage_index") or 0)),
                "active_creature_ids": [
                    int(cid)
                    for cid in (state_data.get("active_creature_ids") or [])
                    if int(cid or 0) > 0
                ],
                "starts_at_ts": float(state_data.get("starts_at_ts") or _dt_to_ts(row.get("started_at"))),
                "music_override_started": bool(state_data.get("music_override_started")),
                "warning_offsets_sent": [
                    int(v)
                    for v in (state_data.get("warning_offsets_sent") or [])
                    if int(v or 0) >= 0
                ],
                "expires_at_ts": _dt_to_ts(row.get("expires_at")),
                "next_announce_at_ts": _dt_to_ts(row.get("next_announce_at")),
                "state": str(state_data.get("phase") or "active").strip().lower() or "active",
                "scene_lines": self._collect_scene_lines(district_ids),
                "room_lines": list(incident_def.get("room_lines") or []),
                "covered_room_ids": self._collect_district_rooms(district_ids),
            }
            if actor["id"] > 0:
                self._active[actor["id"]] = actor

    def _insert_incident_row(
        self,
        *,
        city_key: str,
        incident_key: str,
        district_key: str,
        difficulty: int,
        target_level: int,
        duration_seconds: int,
        stage_index: int,
        next_announce_ts: float,
        expires_at_ts: float,
        state_json: dict,
    ) -> int:
        db = getattr(self.server, "db", None)
        if not db or not db._pool:
            return 0
        conn = db._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO town_trouble_incidents
                    (city_key, incident_key, district_key, state, target_level, difficulty,
                     duration_seconds, stage_index, state_json, expires_at, next_announce_at)
                VALUES
                    (%s, %s, %s, 'active', %s, %s, %s, %s, %s, FROM_UNIXTIME(%s), FROM_UNIXTIME(%s))
                """,
                (
                    city_key,
                    incident_key,
                    district_key,
                    int(target_level),
                    int(difficulty),
                    int(duration_seconds),
                    int(stage_index),
                    _json_dumps(state_json),
                    float(expires_at_ts),
                    float(next_announce_ts),
                ),
            )
            conn.commit()
            return int(cur.lastrowid or 0)
        except Exception as exc:
            log.error("TownTroubleManager: failed creating incident row (%s)", exc, exc_info=True)
            return 0
        finally:
            conn.close()

    def _save_incident_state(self, actor: dict):
        db = getattr(self.server, "db", None)
        if not db or not db._pool or int(actor.get("id") or 0) <= 0:
            return
        payload = self._build_state_payload(actor)
        sql = """
            UPDATE town_trouble_incidents
            SET stage_index = %s, state_json = %s, next_announce_at = FROM_UNIXTIME(%s), updated_at = NOW()
            WHERE id = %s
        """
        params = (
            int(actor.get("stage_index") or 0),
            _json_dumps(payload),
            float(actor.get("next_announce_at_ts") or time.time()),
            int(actor.get("id") or 0),
        )
        if not self._write_async(sql, params):
            db.execute_update(sql, params)

    def _save_resolved_state(self, actor: dict, *, success: bool):
        db = getattr(self.server, "db", None)
        if not db or not db._pool or int(actor.get("id") or 0) <= 0:
            return
        payload = {"active_creature_ids": []}
        sql = """
            UPDATE town_trouble_incidents
            SET state = %s, stage_index = %s, state_json = %s, resolved_at = NOW(), updated_at = NOW()
            WHERE id = %s
        """
        params = (
            "resolved" if success else "failed",
            int(actor.get("stage_index") or 0),
            _json_dumps(payload),
            int(actor.get("id") or 0),
        )
        if not self._write_async(sql, params):
            db.execute_update(sql, params)

    def _build_state_payload(self, actor: dict) -> dict:
        return {
            "phase": str(actor.get("state") or "active"),
            "starts_at_ts": float(actor.get("starts_at_ts") or 0.0),
            "music_override_started": bool(actor.get("music_override_started")),
            "warning_offsets_sent": [
                int(v)
                for v in (actor.get("warning_offsets_sent") or [])
                if int(v or 0) >= 0
            ],
            "active_creature_ids": [
                int(cid)
                for cid in (actor.get("active_creature_ids") or [])
                if int(cid or 0) > 0
            ],
        }

    def _prelude_duration_seconds(self) -> int:
        return max(0, int(self._config.get("prelude_duration_seconds") or 0))

    def _music_lead_seconds(self) -> int:
        return max(0, int(self._config.get("music_lead_seconds") or 0))

    def _warning_definitions(self) -> list[dict]:
        rows = []
        for raw in self._config.get("prelude_warnings") or []:
            if not isinstance(raw, dict):
                continue
            seconds_before_start = max(0, int(raw.get("seconds_before_start") or 0))
            lines = [str(v).strip() for v in (raw.get("lines") or []) if str(v).strip()]
            if seconds_before_start <= 0 or not lines:
                continue
            rows.append({
                "seconds_before_start": seconds_before_start,
                "lines": lines,
            })
        rows.sort(key=lambda row: row["seconds_before_start"], reverse=True)
        return rows

    def _format_countdown(self, seconds_remaining: int) -> str:
        seconds_remaining = max(0, int(seconds_remaining or 0))
        if seconds_remaining >= 60 and seconds_remaining % 60 == 0:
            minutes = seconds_remaining // 60
            return f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
        return f"{seconds_remaining} second" if seconds_remaining == 1 else f"{seconds_remaining} seconds"

    def _should_enable_music_override(self, actor: dict, now: float) -> bool:
        phase = str(actor.get("state") or "").strip().lower()
        if phase == "active":
            return True
        if phase != "prelude":
            return False
        starts_at_ts = float(actor.get("starts_at_ts") or 0.0)
        if starts_at_ts <= 0:
            return False
        return now >= max(0.0, starts_at_ts - float(self._music_lead_seconds()))

    def _emit_due_prelude_warnings(self, actor: dict, now: float) -> bool:
        starts_at_ts = float(actor.get("starts_at_ts") or 0.0)
        if starts_at_ts <= 0:
            return False
        sent = {int(v) for v in (actor.get("warning_offsets_sent") or []) if int(v or 0) >= 0}
        changed = False
        for warning in self._warning_definitions():
            seconds_before_start = int(warning.get("seconds_before_start") or 0)
            if seconds_before_start in sent:
                continue
            if now < starts_at_ts - float(seconds_before_start):
                continue
            sent.add(seconds_before_start)
            actor["warning_offsets_sent"] = sorted(sent, reverse=True)
            line = self._format_line(
                actor,
                random.choice(list(warning.get("lines") or [])),
                key="prelude_warning",
                replacements={"%time_remaining%": self._format_countdown(seconds_before_start)},
            )
            try:
                import asyncio
                loop = asyncio.get_running_loop()
                loop.create_task(self._broadcast_city(int(actor.get("city_zone_id") or 0), line, preset=TextPresets.WARNING))
            except Exception:
                pass
            changed = True
        return changed

    async def _push_sync_for_city(self, zone_id: int):
        zone_id = int(zone_id or 0)
        if zone_id <= 0:
            return
        broadcaster = getattr(self.server, "sync_broadcaster", None)
        if not broadcaster:
            return
        sessions = [
            session
            for session in self.server.sessions.playing()
            if int(getattr(getattr(session, "current_room", None), "zone_id", 0) or 0) == zone_id
        ]
        await broadcaster.broadcast_sessions(sessions)

    def _city_for_zone(self, zone_id: int):
        zone_id = int(zone_id or 0)
        for city_key, city in self._cities.items():
            if int(city.get("zone_id") or 0) == zone_id:
                return city_key, dict(city or {})
        return None, None

    async def _maybe_force_boot_incident(self, session):
        if self._boot_login_started:
            return
        if self._active:
            self._boot_login_started = True
            return
        if not bool(self._config.get("start_on_first_login_after_boot", False)):
            return
        room = getattr(session, "current_room", None)
        zone_id = int(getattr(room, "zone_id", 0) or 0)
        city_key, city = self._city_for_zone(zone_id)
        if not city_key or not city:
            return
        self._boot_login_started = True
        now = time.time()
        self._last_roll_at = now
        await self._start_incident(city_key, city, now)

    def _validate_definitions(self):
        if self._prelude_duration_seconds() > 0 and not self._warning_definitions():
            log.warning("TownTroubleManager: prelude is enabled but no prelude warnings were defined in Lua.")
        default_override = str(self._config.get("default_audio_zone_override") or "").strip()
        if default_override:
            return
        for incident in self._incidents.values():
            if str((incident or {}).get("audio_zone_override") or "").strip():
                continue
            log.warning(
                "TownTroubleManager: incident '%s' has no audio_zone_override and no default city override.",
                str((incident or {}).get("key") or "unknown"),
            )

    def _upsert_participation(self, incident_id: int, character_id: int, *, damage: int, kills: int):
        threshold_damage = max(1, int(self._config.get("min_participation_damage") or 1))
        threshold_kills = max(1, int(self._config.get("min_participation_kills") or 1))
        db = getattr(self.server, "db", None)
        if not db:
            return
        sql = """
            INSERT INTO town_trouble_participants
                (incident_id, character_id, damage_done, kill_count, qualifies)
            VALUES
                (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                damage_done = damage_done + VALUES(damage_done),
                kill_count = kill_count + VALUES(kill_count),
                qualifies = IF((damage_done + VALUES(damage_done)) >= %s OR (kill_count + VALUES(kill_count)) >= %s, 1, qualifies),
                updated_at = NOW()
        """
        params = (
            int(incident_id),
            int(character_id),
            max(0, int(damage or 0)),
            max(0, int(kills or 0)),
            1 if max(0, int(damage or 0)) >= threshold_damage or max(0, int(kills or 0)) >= threshold_kills else 0,
            threshold_damage,
            threshold_kills,
        )
        if not self._write_async(sql, params):
            db.execute_update(sql, params)

    def _queue_rewards(self, actor: dict):
        db = getattr(self.server, "db", None)
        if not db or not db._pool:
            return
        incident_def = self._incident_def(actor)
        rewards = dict(incident_def.get("rewards") or {})
        conn = db._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, character_id, damage_done, kill_count, qualifies
                FROM town_trouble_participants
                WHERE incident_id = %s
                """,
                (int(actor.get("id") or 0),),
            )
            rows = cur.fetchall() or []
        except Exception as exc:
            log.error("TownTroubleManager: failed loading participants (%s)", exc, exc_info=True)
            return
        finally:
            conn.close()

        min_boxes = max(int(self._config.get("min_reward_boxes") or 1), int(rewards.get("box_min") or 0))
        max_boxes = max(min_boxes, int(rewards.get("box_max") or min_boxes))
        max_cap = max(min_boxes, int(self._config.get("max_reward_boxes") or max_boxes))
        length_bonus = 1 if int(actor.get("duration_seconds") or 0) >= 900 else 0
        level_bonus = 1 if int(actor.get("target_level") or 1) >= 20 else 0
        reward_box_level = max(1, int(actor.get("target_level") or 1) + int(rewards.get("box_level_bonus") or 0))

        for row in rows:
            qualifies = bool(int(row.get("qualifies") or 0))
            if not qualifies:
                continue
            box_count = random.randint(min_boxes, max_boxes)
            box_count += max(0, int(actor.get("difficulty") or 1) - 1) + length_bonus + level_bonus
            box_count = max(min_boxes, min(max_cap, box_count))
            payload = {
                "incident_id": int(actor.get("id") or 0),
                "incident_key": str(actor.get("incident_key") or ""),
                "xp": max(0, int(rewards.get("xp") or 0)),
                "fame": max(0, int(rewards.get("fame") or 0)),
                "silver": max(0, int(rewards.get("silver") or 0)),
                "box_count": box_count,
                "box_level": reward_box_level,
                "district_label": str(actor.get("district_label") or "the district"),
            }
            db.execute_update(
                """
                UPDATE town_trouble_participants
                SET reward_payload_json = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (_json_dumps(payload), int(row.get("id") or 0)),
            )

    async def _grant_pending_rewards(self, session, incident_id: int | None = None):
        db = getattr(self.server, "db", None)
        character_id = int(getattr(session, "character_id", 0) or 0)
        if not db or not db._pool or character_id <= 0:
            return
        conn = db._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            sql = """
                SELECT id, incident_id, reward_payload_json
                FROM town_trouble_participants
                WHERE character_id = %s
                  AND reward_payload_json IS NOT NULL
                  AND reward_granted_at IS NULL
            """
            params = [character_id]
            if incident_id:
                sql += " AND incident_id = %s"
                params.append(int(incident_id))
            sql += " ORDER BY id"
            cur.execute(sql, tuple(params))
            rows = cur.fetchall() or []
        except Exception as exc:
            log.error("TownTroubleManager: failed loading pending rewards (%s)", exc, exc_info=True)
            return
        finally:
            conn.close()

        for row in rows:
            payload = _json_loads(row.get("reward_payload_json"), {})
            if not payload:
                continue
            await self._apply_reward_payload(session, payload)
            db.execute_update(
                "UPDATE town_trouble_participants SET reward_granted_at = NOW(), updated_at = NOW() WHERE id = %s",
                (int(row.get("id") or 0),),
            )

    async def _apply_reward_payload(self, session, payload: dict):
        xp = max(0, int(payload.get("xp") or 0))
        fame = max(0, int(payload.get("fame") or 0))
        silver = max(0, int(payload.get("silver") or 0))
        box_count = max(0, int(payload.get("box_count") or 0))
        box_level = max(1, int(payload.get("box_level") or getattr(session, "level", 1) or 1))
        district_label = str(payload.get("district_label") or "the district")

        await session.send_line(colorize(
            f"  Your work during the trouble in {district_label} is recognized with a field reward.",
            TextPresets.SYSTEM,
        ))
        if xp > 0 and hasattr(self.server, "experience"):
            await self.server.experience.award_xp_to_pool(session, xp, source="town_trouble")
        if fame > 0:
            await award_fame(session, self.server, fame, "town_trouble", detail_text=f"Helped resolve trouble in {district_label}.", quiet=False)
        if silver > 0:
            session.silver = int(getattr(session, "silver", 0) or 0) + silver
            await session.send_line(colorize(f"  Silver: +{silver}", TextPresets.SYSTEM))
            if getattr(self.server, "db", None):
                self.server.db.save_character_resources(
                    session.character_id,
                    session.health_current,
                    session.mana_current,
                    session.spirit_current,
                    session.stamina_current,
                    session.silver,
                )
        for _ in range(box_count):
            box = generate_box(getattr(self.server, "db", None), box_level, server=self.server)
            if not box:
                continue
            success, location, fail_msg = auto_stow_item(session, self.server, box)
            if success:
                await session.send_line(colorize(
                    f"  You receive {box.get('name') or 'a coffer'} and tuck it into your {location}.",
                    TextPresets.SYSTEM,
                ))
            else:
                self.server.world.add_ground_item(
                    session.current_room.id,
                    box,
                    dropped_by_character_id=session.character_id,
                    dropped_by_name=session.character_name,
                    source="town_trouble_reward",
                )
                await session.send_line(colorize(
                    f"  {fail_msg}  A reward coffer is set down at your feet instead.",
                    TextPresets.WARNING,
                ))
