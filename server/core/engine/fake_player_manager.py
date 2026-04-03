"""
fake_player_manager.py
----------------------
Synthetic player runtime for ambient city populations.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import re
import time
import concurrent.futures
from collections import deque

from server.core.commands.player.boxpick import _db_claim, _db_complete, _db_get_job, _db_get_pending, _db_submit
from server.core.commands.player.foraging import _consume_room_slot, _match_requested_candidate, _room_forage_candidates, _room_remaining_slots
from server.core.commands.player.shop import _insert_item_into_pawn_backroom, _is_pawn_shop, _load_shop_by_room
from server.core.engine.fake_player_planner import plan_actor_action
from server.core.engine.treasure import generate_box, generate_gem, generate_scroll
from server.core.entity.fake_player.synthetic_player import SyntheticPlayer
from server.core.protocol.colors import TextPresets, colorize, speech

log = logging.getLogger(__name__)

_GREETING_WORDS = {"hello", "hi", "hey", "greetings", "hail", "sup", "yo"}
_INSULT_WORDS = {"idiot", "moron", "trash", "stupid", "ugly", "sucks", "loser", "jerk"}
_AFFECTION_WORDS = {"thanks", "thank", "appreciate", "cheers", "welcome", "friend"}
_LAWBREAKING_CHARGES = ("impropriety", "hooliganism", "theft")
_OPPOSITES = {
    "north": "south", "south": "north",
    "east": "west", "west": "east",
    "northeast": "southwest", "southwest": "northeast",
    "northwest": "southeast", "southeast": "northwest",
    "up": "below", "down": "above",
    "out": "inside",
}
_SPEECH_PREFIX_RE = re.compile(r'^(?P<verb>[a-z]+),\s*"(?P<message>.*)"$', re.IGNORECASE)
_INLINE_SPEECH_RE = re.compile(r'^(?P<text>.+?)\s+(?P<verb>says|asks|mutters|snorts|growls|murmurs|whispers|yells|shouts),\s*"(?P<message>.*)"$', re.IGNORECASE)
_EMOTE_LEADS = (
    "adjusts", "brushes", "checks", "fidgets", "gasps", "gives", "glances", "goes",
    "helps", "keeps", "kicks", "leans", "nods", "offers", "pretends", "signals",
    "spreads", "squints", "starts", "stretches", "studies", "tests",
)


def _now() -> float:
    return time.time()


def _clamp(value, low, high):
    return max(low, min(high, value))


def _json_dumps(value) -> str:
    return json.dumps(value or {}, separators=(",", ":"), ensure_ascii=True)


def _json_loads(raw, default):
    if raw in (None, ""):
        return default
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return default


def _serialize_status_effects(effects: dict) -> dict:
    out = {}
    for key, value in dict(effects or {}).items():
        if isinstance(value, dict):
            out[str(key)] = value
            continue
        out[str(key)] = {
            "effect_id": getattr(value, "effect_id", str(key)),
            "expires": getattr(value, "expires", -1),
            "stacks": getattr(value, "stacks", 1),
            "magnitude": getattr(value, "magnitude", 1.0),
            "tick_interval": getattr(value, "tick_interval", 0),
            "data": dict(getattr(value, "data", {}) or {}),
        }
    return out


def _place_in_free_hand_synthetic(actor, item_row: dict):
    if not getattr(actor, "right_hand", None):
        hand_attr = "right_hand"
        slot_name = "right_hand"
    elif not getattr(actor, "left_hand", None):
        hand_attr = "left_hand"
        slot_name = "left_hand"
    else:
        return None

    item = {
        "item_id": int(item_row.get("id") or item_row.get("item_id") or 0),
        "id": int(item_row.get("id") or item_row.get("item_id") or 0),
        "inv_id": None,
        "name": item_row.get("name"),
        "short_name": item_row.get("short_name"),
        "noun": item_row.get("noun"),
        "article": item_row.get("article") or "a",
        "item_type": item_row.get("item_type") or "forage",
        "slot": slot_name,
        "container_id": None,
    }
    setattr(actor, hand_attr, item)
    return hand_attr


class FakePlayerManager:
    def __init__(self, server):
        self.server = server
        self._cfg = {}
        self._defaults = {}
        self._regions = {}
        self._dialogue = {}
        self._dialogue_builders = {}
        self._dialogue_builder_disabled_keys: set[str] = set()
        self._argument_topics = {}
        self._intent_tokens = {}
        self._names = {}
        self._mbti = {}
        self._gear = {}
        self._races = []
        self._professions = []
        self._archetypes = []
        self._actors: dict[int, SyntheticPlayer] = {}
        self._actor_ids_by_character: dict[int, int] = {}
        self._service_rooms = {"inn": set(), "pawn": set(), "locksmith": set()}
        self._last_save_at = 0.0
        self._justice_id_offset = 1000000000
        self._population_target = 0
        self._population_target_until = 0.0
        self._next_spawn_batch_at = 0.0
        self._session_region_keys: dict[int, str] = {}
        self._active_region_keys: set[str] = set()
        self._active_scope_rooms: set[int] = set()
        self._active_scope_anchors: list[int] = []
        self._item_template_cache: dict[str, dict | None] = {}
        self._recent_dialogue_global: dict[str, float] = {}
        self._dirty_dialogue_global: dict[str, float] = {}
        self._pair_social_until: dict[str, float] = {}
        self._room_arguments: dict[int, dict] = {}
        self._room_conversations: dict[int, dict] = {}
        self._room_prompts: dict[int, dict] = {}
        self._player_chat_state: dict[int, dict] = {}
        self._planner_pool = None
        self._planner_futures: dict[int, concurrent.futures.Future] = {}
        self._path_cache: dict[tuple[int, int], tuple[float, list[int]]] = {}
        self._distance_cache: dict[tuple[int, int], tuple[float, int]] = {}
        self._perf = {"tick_ms": 0.0, "planner_submit": 0, "planner_done": 0, "path_cache_hit": 0, "path_cache_miss": 0}
        self._last_perf_log_at = 0.0

    async def initialize(self):
        self._cfg = getattr(self.server.lua, "get_fake_players", lambda: {})() or {}
        self._defaults = dict(self._cfg.get("defaults") or {})
        self._regions = dict(self._cfg.get("regions") or {})
        self._dialogue = dict(self._cfg.get("dialogue") or {})
        self._dialogue_builders = dict(self._cfg.get("dialogue_builders") or {})
        self._dialogue_builder_disabled_keys = {
            str(row or "").strip()
            for row in (self._defaults.get("dialogue_builder_disabled_keys") or [])
            if str(row or "").strip()
        }
        self._argument_topics = dict(self._cfg.get("argument_topics") or {})
        self._intent_tokens = dict(self._cfg.get("intent_tokens") or {})
        self._names = dict(self._cfg.get("names") or {})
        self._mbti = {str(k).upper(): dict(v or {}) for k, v in (self._cfg.get("mbti") or {}).items()}
        self._gear = dict(self._cfg.get("gear") or {})
        self._races = list(self._cfg.get("races") or [])
        self._professions = list(self._cfg.get("professions") or [])
        raw_archetypes = self._cfg.get("archetypes") or {}
        if isinstance(raw_archetypes, dict):
            self._archetypes = []
            for key, row in raw_archetypes.items():
                if not isinstance(row, dict):
                    continue
                merged = dict(row)
                merged.setdefault("key", str(key).strip().lower())
                self._archetypes.append(merged)
        else:
            self._archetypes = list(raw_archetypes or [])
        self._justice_id_offset = int(self._defaults.get("justice_id_offset") or 1000000000)
        self._refresh_service_rooms()
        self._load_global_dialogue_history()
        self._load_active_rows()
        self._init_planner_pool()
        self._last_perf_log_at = _now()
        log.info("FakePlayerManager ready (%d cached actors, %d regions)", len(self._actors), len(self._regions))

    def get_all(self) -> list[SyntheticPlayer]:
        return list(self._actors.values())

    def shutdown(self):
        pool = self._planner_pool
        self._planner_pool = None
        if pool:
            try:
                pool.shutdown(wait=False, cancel_futures=True)
            except Exception:
                log.debug("Fake player planner pool shutdown failed", exc_info=True)

    def _init_planner_pool(self):
        workers = max(0, int(self._defaults.get("planner_workers") or 0))
        if workers <= 0:
            self._planner_pool = None
            return
        cpu_total = max(1, int(os.cpu_count() or 1))
        workers = max(1, min(workers, max(1, cpu_total - 1)))
        self._planner_pool = concurrent.futures.ProcessPoolExecutor(max_workers=workers)
        log.info("FakePlayerManager planner pool ready (%d worker processes)", workers)

    def _plan_queue_limit(self) -> int:
        workers = max(1, int(self._defaults.get("planner_workers") or 1))
        return max(1, workers * max(1, int(self._defaults.get("planner_queue_multiplier") or 4)))

    def _cached_path(self, from_room_id: int, to_room_id: int) -> list[int]:
        key = (int(from_room_id or 0), int(to_room_id or 0))
        if key[0] <= 0 or key[1] <= 0:
            return []
        now = _now()
        ttl = max(1.0, float(self._defaults.get("path_cache_seconds") or 45))
        cached = self._path_cache.get(key)
        if cached and cached[0] > now:
            self._perf["path_cache_hit"] += 1
            return list(cached[1])
        self._perf["path_cache_miss"] += 1
        path = list(self.server.world.find_path(key[0], key[1]) or [])
        self._path_cache[key] = (now + ttl, path)
        return path

    def _cached_distance(self, from_room_id: int, to_room_id: int) -> int:
        key = (int(from_room_id or 0), int(to_room_id or 0))
        if key[0] <= 0 or key[1] <= 0:
            return 10**9
        now = _now()
        ttl = max(1.0, float(self._defaults.get("distance_cache_seconds") or 90))
        cached = self._distance_cache.get(key)
        if cached and cached[0] > now:
            return int(cached[1])
        path = self._cached_path(key[0], key[1])
        distance = max(0, len(path) - 1) if path else 10**9
        self._distance_cache[key] = (now + ttl, distance)
        return distance

    def in_room(self, room_id: int) -> list[SyntheticPlayer]:
        room_id = int(room_id or 0)
        return [actor for actor in self._actors.values() if getattr(getattr(actor, "current_room", None), "id", 0) == room_id]

    async def tick(self, tick_count: int):
        if tick_count % 10 != 0:
            return
        tick_start = _now()
        now = _now()
        self._refresh_service_rooms()
        bubble_rooms, bubble_anchors = self._active_bubble()
        self._cull_outside_bubble(bubble_rooms)
        if bubble_rooms:
            self._ensure_population(bubble_rooms, bubble_anchors, now)
        tick_context = self._build_tick_context(bubble_rooms)
        self._collect_finished_plans()
        planner_submits_left = max(1, int(self._defaults.get("planner_submit_per_tick") or 18))
        actor_updates_left = max(1, int(self._defaults.get("actor_updates_per_tick") or 18))
        for actor in list(self._actors.values()):
            try:
                used_update, used_submit = await self._tick_actor(actor, bubble_rooms, bubble_anchors, now, tick_context, planner_submits_left, actor_updates_left)
                planner_submits_left = max(0, planner_submits_left - used_submit)
                actor_updates_left = max(0, actor_updates_left - used_update)
            except Exception:
                log.exception("Fake player tick failed for %s", getattr(actor, "character_name", "?"))
        if now - self._last_save_at >= float(self._defaults.get("save_interval_sec") or 90):
            self._save_all()
            self._last_save_at = now
        self._perf["tick_ms"] += (_now() - tick_start) * 1000.0
        perf_interval = max(5.0, float(self._defaults.get("perf_log_interval_seconds") or 60))
        if now - self._last_perf_log_at >= perf_interval:
            log.info(
                "FakePlayer perf: avg_tick_ms=%.2f planner_submit=%d planner_done=%d path_cache(hit=%d miss=%d) actors=%d",
                float(self._perf["tick_ms"]) / max(1.0, perf_interval),
                int(self._perf["planner_submit"]),
                int(self._perf["planner_done"]),
                int(self._perf["path_cache_hit"]),
                int(self._perf["path_cache_miss"]),
                len(self._actors),
            )
            self._perf = {"tick_ms": 0.0, "planner_submit": 0, "planner_done": 0, "path_cache_hit": 0, "path_cache_miss": 0}
            self._last_perf_log_at = now

    def on_player_login(self, session):
        room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
        if room_id <= 0:
            return
        session_key = int(getattr(session, "id", 0) or 0)
        if session_key <= 0:
            return
        region_key = self._nearest_city_region_key(room_id) or self._closest_region_key(room_id)
        if not region_key:
            return
        self._session_region_keys[session_key] = region_key
        self._rebuild_active_scope()

    def on_player_logout(self, session):
        session_key = int(getattr(session, "id", 0) or 0)
        if session_key > 0:
            self._session_region_keys.pop(session_key, None)
        self._rebuild_active_scope()

    async def on_player_social(self, session, kind: str, message: str = "", *, target=None):
        room = getattr(session, "current_room", None)
        if not room:
            return
        spam_event = self._track_player_chat(session, kind, message)
        direct_target = target if getattr(target, "is_synthetic_player", False) else None
        actors = self.in_room(room.id)
        if direct_target and direct_target not in actors:
            actors.append(direct_target)
        for actor in actors:
            if actor.is_dead or actor.in_combat:
                continue
            if direct_target and actor is not direct_target:
                continue
            if not direct_target and random.random() > float(self._personality(actor, "player_reply", 0.25)):
                continue
            memory = self._memory_row(actor, getattr(session, "character_id", 0))
            lowered = str(message or "").lower()
            delta = 0
            if any(word in lowered for word in _GREETING_WORDS):
                delta += 1
            if any(word in lowered for word in _AFFECTION_WORDS):
                delta += 1
            if any(word in lowered for word in _INSULT_WORDS):
                delta -= 2
            if actor.character_name.lower() in lowered:
                delta += 1
            memory["affinity"] = _clamp(int(memory.get("affinity") or 0) + delta, -10, 10)
            memory["interaction_count"] = int(memory.get("interaction_count") or 0) + 1
            memory["last_topic"] = str(kind or "")
            actor.synthetic_flags.setdefault("memory", {})[str(getattr(session, "character_id", 0))] = memory
            reaction_kind = "spam" if spam_event and random.random() < max(0.12, float(self._personality(actor, "rude", 0.12)) * 0.9) else str(kind or "")
            actor.synthetic_flags["pending_reaction"] = {
                "player_name": getattr(session, "character_name", "someone"),
                "player_id": int(getattr(session, "character_id", 0) or 0),
                "kind": reaction_kind,
                "message": str(message or ""),
                "direct": bool(direct_target is actor),
                "spam_event": dict(spam_event or {}),
            }

    def _refresh_service_rooms(self):
        self._service_rooms["inn"] = {int(rid) for rid in getattr(getattr(self.server, "inns", None), "_front_desks", {}).keys()}
        locksmith = set()
        pawn = set()
        npcs = getattr(getattr(self.server, "npcs", None), "get_all_npcs", lambda: [])()
        for npc in npcs or []:
            room_id = int(getattr(npc, "room_id", 0) or 0)
            if room_id <= 0:
                continue
            if getattr(npc, "matches_service", None) and npc.matches_service("locksmith"):
                locksmith.add(room_id)
            if getattr(npc, "matches_service", None) and npc.matches_service("pawnbroker"):
                pawn.add(room_id)
        if getattr(self.server, "db", None):
            for row in self.server.db.execute_query("SELECT room_id FROM shops WHERE LOWER(shop_type) = 'pawn'"):
                try:
                    pawn.add(int(row[0]))
                except Exception:
                    continue
        self._service_rooms["locksmith"] = locksmith
        self._service_rooms["pawn"] = pawn

    def _active_bubble(self) -> tuple[set[int], list[int]]:
        self._bootstrap_active_scope_from_sessions()
        return set(self._active_scope_rooms), list(self._active_scope_anchors)

    def _reachable_rooms(self, start_room_id: int, max_distance: int) -> set[int]:
        start_room_id = int(start_room_id or 0)
        if start_room_id <= 0:
            return set()
        visited = {start_room_id}
        queue = deque([(start_room_id, 0)])
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

    def _load_active_rows(self):
        for row in self._fetch_rows("SELECT * FROM synthetic_players_state WHERE active = 1 ORDER BY id ASC"):
            actor = self._actor_from_row(row)
            if not actor:
                continue
            self._actors[actor.synthetic_id] = actor
            self._actor_ids_by_character[actor.character_id] = actor.synthetic_id

    def _bootstrap_active_scope_from_sessions(self):
        sessions = list(getattr(getattr(self.server, "sessions", None), "playing", lambda: [])())
        current_session_ids = {int(getattr(session, "id", 0) or 0) for session in sessions if int(getattr(session, "id", 0) or 0) > 0}
        stale_ids = [session_id for session_id in self._session_region_keys.keys() if session_id not in current_session_ids]
        for session_id in stale_ids:
            self._session_region_keys.pop(session_id, None)
        changed = False
        for session in sessions:
            session_id = int(getattr(session, "id", 0) or 0)
            room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
            if session_id <= 0 or room_id <= 0 or session_id in self._session_region_keys:
                continue
            region_key = self._nearest_city_region_key(room_id) or self._closest_region_key(room_id)
            if not region_key:
                continue
            self._session_region_keys[session_id] = region_key
            changed = True
        if changed or (sessions and not self._active_scope_rooms) or (not sessions and self._active_scope_rooms):
            self._rebuild_active_scope()

    def _rebuild_active_scope(self):
        radius = max(10, int(self._defaults.get("login_city_scope_radius") or 140))
        region_keys = {str(key).strip().lower() for key in self._session_region_keys.values() if str(key).strip().lower() in self._regions}
        self._active_region_keys = region_keys
        if not region_keys:
            self._active_scope_rooms = set()
            self._active_scope_anchors = []
            return
        rooms: set[int] = set()
        anchors: list[int] = []
        for region_key in sorted(region_keys):
            region = dict(self._regions.get(region_key) or {})
            region_anchor_ids = [int(rid) for rid in (region.get("anchor_room_ids") or []) if int(rid or 0) > 0]
            if not region_anchor_ids:
                region_anchor_ids = [int(rid) for rid in (region.get("hotspot_room_ids") or []) if int(rid or 0) > 0]
            anchors.extend(region_anchor_ids)
            for field in ("anchor_room_ids", "hotspot_room_ids", "rest_room_ids", "travel_room_ids", "crafting_room_ids"):
                rooms.update(int(rid) for rid in (region.get(field) or []) if int(rid or 0) > 0)
            for anchor_room_id in region_anchor_ids:
                rooms.update(self._reachable_rooms(anchor_room_id, radius))
        self._active_scope_rooms = rooms
        self._active_scope_anchors = list(dict.fromkeys(anchors))

    def _cull_outside_bubble(self, bubble_rooms: set[int]):
        if not bubble_rooms:
            for actor in list(self._actors.values()):
                self._deactivate_actor(actor)
        return

    def _ensure_population(self, bubble_rooms: set[int], anchors: list[int], now: float):
        sessions = list(getattr(self.server, "sessions", None).playing())
        if not sessions:
            return
        desired = self._desired_population(sessions, bubble_rooms, anchors)
        if len(self._actors) < desired and now >= float(self._next_spawn_batch_at or 0.0):
            batch_size = max(1, int(self._defaults.get("spawn_batch_size") or 5))
            spawned = 0
            while len(self._actors) < desired and spawned < batch_size:
                actor = self._activate_or_create_actor(bubble_rooms, anchors)
                if not actor:
                    break
                spawned += 1
            if spawned > 0:
                self._next_spawn_batch_at = now + max(1.0, float(self._defaults.get("spawn_batch_interval_seconds") or 2))
        while len(self._actors) > desired:
            actor = self._pick_trim_actor(anchors)
            if not actor:
                break
            self._deactivate_actor(actor)

    def _desired_population(self, sessions, bubble_rooms: set[int], anchors: list[int]) -> int:
        base = int(len(sessions) * int(self._defaults.get("population_per_player") or 7))
        base = max(int(self._defaults.get("min_population_with_players") or 6), base)
        kind = self._population_kind(bubble_rooms, anchors)
        floor, ceiling = self._population_bounds(kind)
        base = min(base, ceiling)
        refresh_seconds = max(15, int(self._defaults.get("population_target_refresh_seconds") or 180))
        now = _now()
        if (
            self._population_target_until <= now
            or self._population_target < floor
            or self._population_target > ceiling
        ):
            lower = max(floor, base)
            upper = max(lower, ceiling)
            self._population_target = random.randint(lower, upper)
            self._population_target_until = now + refresh_seconds
        return int(self._population_target)

    def _population_kind(self, bubble_rooms: set[int], anchors: list[int]) -> str:
        if self._active_region_keys:
            best_rank = -1
            best_kind = "wilds"
            for region_key in self._active_region_keys:
                region = dict(self._regions.get(region_key) or {})
                kind = str(region.get("kind") or "wilds").strip().lower() or "wilds"
                rank = {"wilds": 0, "town": 1, "city": 2}.get(kind, 0)
                if rank > best_rank:
                    best_rank = rank
                    best_kind = kind
            return best_kind
        best_rank = -1
        best_kind = "wilds"
        for region in self._regions.values():
            kind = str(region.get("kind") or "wilds").strip().lower() or "wilds"
            rank = {"wilds": 0, "town": 1, "city": 2}.get(kind, 0)
            region_rooms = set()
            for key in ("hotspot_room_ids", "rest_room_ids", "anchor_room_ids", "travel_room_ids", "crafting_room_ids"):
                region_rooms.update(int(rid) for rid in (region.get(key) or []) if int(rid or 0) > 0)
            if not region_rooms:
                continue
            if anchors and any(int(anchor or 0) in region_rooms for anchor in anchors):
                if rank > best_rank:
                    best_rank = rank
                    best_kind = kind
                continue
            if bubble_rooms and (region_rooms & bubble_rooms) and rank > best_rank:
                best_rank = rank
                best_kind = kind
        return best_kind

    def _population_bounds(self, kind: str) -> tuple[int, int]:
        kind = str(kind or "wilds").strip().lower()
        floor = int(self._defaults.get(f"{kind}_population_floor") or 0)
        ceiling = int(self._defaults.get(f"{kind}_population_ceiling") or 0)
        if floor <= 0:
            floor = int(self._defaults.get("min_population_with_players") or 6)
        if ceiling <= 0:
            ceiling = int(self._defaults.get("max_total_population") or 36)
        ceiling = min(ceiling, int(self._defaults.get("max_total_population") or ceiling))
        if ceiling < floor:
            ceiling = floor
        return floor, ceiling

    def _pick_trim_actor(self, anchors: list[int]) -> SyntheticPlayer | None:
        if not self._actors:
            return None
        if self._active_region_keys:
            off_region = [actor for actor in self._actors.values() if str(getattr(actor, "home_region_key", "") or "").strip().lower() not in self._active_region_keys]
            if off_region:
                return random.choice(off_region)
        if not anchors:
            return random.choice(list(self._actors.values()))
        ranked = sorted(
            self._actors.values(),
            key=lambda actor: (
                self._distance_to_anchor(int(getattr(getattr(actor, "current_room", None), "id", 0) or actor.current_room_id or 0), anchors),
                random.random(),
            ),
            reverse=True,
        )
        return ranked[0] if ranked else None

    def _distance_to_anchor(self, room_id: int, anchors: list[int]) -> int:
        room_id = int(room_id or 0)
        if room_id <= 0 or not anchors:
            return 10**9
        best = 10**9
        for anchor in anchors:
            best = min(best, self._cached_distance(int(anchor or 0), room_id))
        return best

    def _activate_or_create_actor(self, bubble_rooms: set[int], anchors: list[int]) -> SyntheticPlayer | None:
        row = self._fetch_one("SELECT * FROM synthetic_players_state WHERE active = 0 ORDER BY updated_at ASC, id ASC LIMIT 1")
        if row:
            actor = self._actor_from_row(row)
            if actor:
                self._actors[actor.synthetic_id] = actor
                self._actor_ids_by_character[actor.character_id] = actor.synthetic_id
                self._activate_existing_actor(actor, self._pick_spawn_room(bubble_rooms, anchors))
                return actor
        created = self._create_actor_row(bubble_rooms, anchors)
        if not created:
            return None
        actor = self._actor_from_row(created)
        if not actor:
            return None
        self._actors[actor.synthetic_id] = actor
        self._actor_ids_by_character[actor.character_id] = actor.synthetic_id
        self._place_actor(actor, int(created.get("current_room_id") or 0))
        return actor

    def _activate_existing_actor(self, actor: SyntheticPlayer, room_id: int):
        room_id = int(room_id or actor.home_room_id or actor.current_room_id or 0)
        actor.connected = True
        actor.state = "playing"
        actor.synthetic_flags.setdefault("memory", self._load_memory(actor.synthetic_id))
        actor.synthetic_flags["intent"] = "idle"
        actor.synthetic_flags["next_action_at"] = _now() + random.uniform(1.0, 6.0)
        self._place_actor(actor, room_id)
        self._execute("UPDATE synthetic_players_state SET active = 1, current_room_id = %s, updated_at = NOW() WHERE id = %s", (room_id, actor.synthetic_id))

    def _deactivate_actor(self, actor: SyntheticPlayer):
        self._save_actor(actor, active=0)
        room = getattr(actor, "current_room", None)
        if room:
            self.server.world.remove_player_from_room(actor, room.id)
        actor.current_room = None
        actor.connected = False
        self._save_memory(actor)
        self._actors.pop(actor.synthetic_id, None)
        self._actor_ids_by_character.pop(actor.character_id, None)

    def _place_actor(self, actor: SyntheticPlayer, room_id: int):
        room = self.server.world.get_room(int(room_id or 0))
        if not room:
            return
        old_room = getattr(actor, "current_room", None)
        if old_room and getattr(old_room, "id", 0) == room.id:
            return
        if old_room:
            self.server.world.remove_player_from_room(actor, old_room.id)
        actor.previous_room = old_room
        actor.current_room = room
        actor.current_room_id = room.id
        self.server.world.add_player_to_room(actor, room.id)

    def _actor_from_row(self, row: dict) -> SyntheticPlayer | None:
        if not row:
            return None
        payload = dict(row)
        payload["inventory"] = _json_loads(payload.get("inventory_json"), [])
        payload["right_hand"] = _json_loads(payload.get("right_hand_json"), None)
        payload["left_hand"] = _json_loads(payload.get("left_hand_json"), None)
        payload["skills"] = _json_loads(payload.get("skills_json"), {})
        payload["injuries"] = _json_loads(payload.get("injuries_json"), {})
        payload["status_effects"] = {}
        payload["wounds"] = _json_loads(payload.get("wounds_json"), {})
        payload["state_json"] = _json_loads(payload.get("state_json"), {})
        actor = SyntheticPlayer(self, payload)
        self._ensure_actor_loadout(actor)
        actor.synthetic_flags.setdefault("memory", self._load_memory(actor.synthetic_id))
        actor.synthetic_flags.setdefault("intent", "idle")
        actor.synthetic_flags.setdefault("next_action_at", _now() + random.uniform(2.0, 8.0))
        if int(row.get("active") or 0):
            room_id = int(payload.get("current_room_id") or payload.get("home_room_id") or 0)
            if room_id > 0:
                self._place_actor(actor, room_id)
        return actor

    def _load_memory(self, synthetic_player_id: int) -> dict:
        rows = self._fetch_rows(
            "SELECT player_character_id, affinity, interaction_count, last_topic, memory_json FROM synthetic_player_memory WHERE synthetic_player_id = %s",
            (synthetic_player_id,),
        )
        out = {}
        for row in rows:
            player_id = int(row.get("player_character_id") or 0)
            out[str(player_id)] = {
                "player_character_id": player_id,
                "affinity": int(row.get("affinity") or 0),
                "interaction_count": int(row.get("interaction_count") or 0),
                "last_topic": str(row.get("last_topic") or ""),
                "memory": _json_loads(row.get("memory_json"), {}),
            }
        return out

    def _memory_row(self, actor: SyntheticPlayer, player_character_id: int) -> dict:
        memory = actor.synthetic_flags.setdefault("memory", {})
        key = str(int(player_character_id or 0))
        row = dict(memory.get(key) or {})
        row.setdefault("player_character_id", int(player_character_id or 0))
        row.setdefault("affinity", 0)
        row.setdefault("interaction_count", 0)
        row.setdefault("last_topic", "")
        memory[key] = row
        return row

    def _save_memory(self, actor: SyntheticPlayer):
        memory = actor.synthetic_flags.get("memory") or {}
        if not getattr(self.server, "db", None):
            return
        conn = self.server.db._get_conn()
        try:
            cur = conn.cursor()
            for row in memory.values():
                cur.execute(
                    """
                    INSERT INTO synthetic_player_memory
                        (synthetic_player_id, player_character_id, affinity, interaction_count, last_topic, memory_json)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        affinity = VALUES(affinity),
                        interaction_count = VALUES(interaction_count),
                        last_topic = VALUES(last_topic),
                        memory_json = VALUES(memory_json),
                        updated_at = NOW()
                    """,
                    (
                        actor.synthetic_id,
                        int(row.get("player_character_id") or 0),
                        int(row.get("affinity") or 0),
                        int(row.get("interaction_count") or 0),
                        str(row.get("last_topic") or ""),
                        _json_dumps(row.get("memory") or {}),
                    ),
                )
        finally:
            conn.close()

    def _save_all(self):
        for actor in list(self._actors.values()):
            self._save_actor(actor, active=1)
            self._save_memory(actor)
        self._flush_global_dialogue_history()

    def _save_actor(self, actor: SyntheticPlayer, *, active: int):
        row = actor.to_state_row()
        self._execute(
            """
            UPDATE synthetic_players_state
            SET active = %s,
                character_name = %s,
                race_id = %s,
                race_name = %s,
                profession_id = %s,
                profession_name = %s,
                gender = %s,
                age = %s,
                level = %s,
                level_target = %s,
                mbti = %s,
                archetype = %s,
                home_region_key = %s,
                home_room_id = %s,
                current_room_id = %s,
                health_current = %s,
                health_max = %s,
                mana_current = %s,
                mana_max = %s,
                spirit_current = %s,
                spirit_max = %s,
                stamina_current = %s,
                stamina_max = %s,
                silver = %s,
                experience = %s,
                field_experience = %s,
                position = %s,
                stance = %s,
                hidden = %s,
                sneaking = %s,
                in_combat = %s,
                is_dead = %s,
                death_room_id = %s,
                death_stat_mult = %s,
                roundtime_end = %s,
                stat_strength = %s,
                stat_constitution = %s,
                stat_dexterity = %s,
                stat_agility = %s,
                stat_discipline = %s,
                stat_aura = %s,
                stat_logic = %s,
                stat_intuition = %s,
                stat_wisdom = %s,
                stat_influence = %s,
                inventory_json = %s,
                right_hand_json = %s,
                left_hand_json = %s,
                skills_json = %s,
                injuries_json = %s,
                status_effects_json = %s,
                wounds_json = %s,
                state_json = %s,
                updated_at = NOW()
            WHERE id = %s
            """,
            (
                int(active),
                row["character_name"],
                row["race_id"],
                row["race_name"],
                row["profession_id"],
                row["profession_name"],
                row["gender"],
                row["age"],
                row["level"],
                row["level_target"],
                row["mbti"],
                row["archetype"],
                row["home_region_key"],
                row["home_room_id"],
                row["current_room_id"],
                row["health_current"],
                row["health_max"],
                row["mana_current"],
                row["mana_max"],
                row["spirit_current"],
                row["spirit_max"],
                row["stamina_current"],
                row["stamina_max"],
                row["silver"],
                row["experience"],
                row["field_experience"],
                row["position"],
                row["stance"],
                row["hidden"],
                row["sneaking"],
                row["in_combat"],
                row["is_dead"],
                row["death_room_id"],
                row["death_stat_mult"],
                row["roundtime_end"],
                row["stat_strength"],
                row["stat_constitution"],
                row["stat_dexterity"],
                row["stat_agility"],
                row["stat_discipline"],
                row["stat_aura"],
                row["stat_logic"],
                row["stat_intuition"],
                row["stat_wisdom"],
                row["stat_influence"],
                _json_dumps(row["inventory"]),
                _json_dumps(row["right_hand"]),
                _json_dumps(row["left_hand"]),
                _json_dumps(row["skills"]),
                _json_dumps(row["injuries"]),
                _json_dumps(_serialize_status_effects(row["status_effects"])),
                _json_dumps(row["wounds"]),
                _json_dumps(row["state_json"]),
                actor.synthetic_id,
            ),
        )

    async def _tick_actor(self, actor: SyntheticPlayer, bubble_rooms: set[int], anchors: list[int], now: float, tick_context: dict, planner_submits_left: int, actor_updates_left: int):
        if not actor.connected or actor.state != "playing":
            return 0, 0
        if actor.is_dead:
            if not actor.synthetic_flags.get("beefy_started"):
                actor.synthetic_flags["beefy_started"] = True
                await self.server.death._begin_ghost_route(actor)
            return 1, 0
        if actor.death_stat_mult < 1.0:
            await self.server.death.stat_penalty_tick(actor)
        active_case = getattr(self.server, "justice", None).get_active_case(actor) if getattr(self.server, "justice", None) else None
        status = str(active_case.get("status") or "") if active_case else ""
        if status in {"incarcerated", "service", "awaiting_sentence"}:
            actor.synthetic_flags["next_action_at"] = now + random.uniform(6.0, 12.0)
            return 1, 0
        self._passive_recovery(actor, now)
        if actor.in_combat:
            await self._combat_tick(actor, now)
            return 1, 0
        reaction = actor.synthetic_flags.get("pending_reaction")
        if reaction and now >= float(actor.synthetic_flags.get("next_action_at") or 0):
            if await self._perform_reaction(actor, reaction):
                actor.synthetic_flags.pop("pending_reaction", None)
                actor.synthetic_flags["next_action_at"] = now + random.uniform(8.0, 18.0)
                return 1, 0
        if now < float(actor.synthetic_flags.get("next_action_at") or 0):
            return 0, 0
        if actor_updates_left <= 0:
            actor.synthetic_flags["next_action_at"] = now + random.uniform(0.6, 1.6)
            return 0, 0
        plan = actor.synthetic_flags.pop("planned_action", None)
        if plan:
            did = await self._execute_planned_action(actor, plan, bubble_rooms, anchors, active_case, now)
            delay_min = float((plan or {}).get("delay_min") or self._defaults.get("expensive_action_min_seconds") or 12)
            delay_max = float((plan or {}).get("delay_max") or self._defaults.get("expensive_action_max_seconds") or 26)
            actor.synthetic_flags["next_action_at"] = now + random.uniform(delay_min, max(delay_min, delay_max))
            return 1 if did else 1, 0
        if actor.synthetic_id in self._planner_futures:
            actor.synthetic_flags["next_action_at"] = now + random.uniform(0.4, 1.2)
            return 0, 0
        if self._planner_pool and planner_submits_left > 0:
            if self._submit_plan(actor, bubble_rooms, active_case, now, tick_context):
                actor.synthetic_flags["next_action_at"] = now + random.uniform(0.4, 1.2)
                return 0, 1
        await self._choose_action(actor, bubble_rooms, anchors, active_case, now)
        return 1, 0

    def _passive_recovery(self, actor: SyntheticPlayer, now: float):
        last = float(actor.synthetic_flags.get("last_passive_tick") or 0)
        if now - last < 30.0:
            return
        actor.synthetic_flags["last_passive_tick"] = now
        room = getattr(actor, "current_room", None)
        if not room:
            return
        rest_mult = 1.0
        if actor.position in {"sitting", "lying", "sleeping"}:
            rest_mult = 1.5
        if getattr(room, "safe", False):
            rest_mult += 0.25
        actor.health_current = min(actor.health_max, actor.health_current + max(1, int((2 + actor.level // 6) * rest_mult)))
        actor.mana_current = min(actor.mana_max, actor.mana_current + max(0, int((1 + actor.level // 12) * rest_mult)))
        actor.stamina_current = min(actor.stamina_max, actor.stamina_current + max(1, int((2 + actor.level // 10) * rest_mult)))
        if actor.position == "sleeping":
            actor.field_experience += int(self._defaults.get("sleep_field_xp_gain") or 90)
        elif getattr(room, "safe", False):
            actor.field_experience += int(self._defaults.get("idle_field_xp_gain") or 25)

    def _build_tick_context(self, bubble_rooms: set[int]) -> dict:
        room_synth_counts: dict[int, int] = {}
        for actor in self._actors.values():
            room_id = int(getattr(getattr(actor, "current_room", None), "id", 0) or getattr(actor, "current_room_id", 0) or 0)
            if room_id > 0:
                room_synth_counts[room_id] = room_synth_counts.get(room_id, 0) + 1

        room_player_counts: dict[int, int] = {}
        for session in self.server.sessions.playing():
            room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
            if room_id > 0:
                room_player_counts[room_id] = room_player_counts.get(room_id, 0) + 1

        hunt_candidates = []
        forage_candidates = []
        room_safe: dict[int, bool] = {}
        for room_id in set(bubble_rooms or set()):
            room = self.server.world.get_room(room_id)
            if not room:
                continue
            room_safe[int(room_id)] = bool(getattr(room, "safe", False))
            if not room_safe[int(room_id)]:
                creatures = [c for c in self.server.creatures.get_creatures_in_room(room_id) if getattr(c, "alive", False)]
                if creatures:
                    levels = [int(getattr(c, "level", 1) or 1) for c in creatures]
                    hunt_candidates.append({
                        "room_id": int(room_id),
                        "min_level": min(levels),
                        "max_level": max(levels),
                    })
                room_lich_uid = int(getattr(room, "lich_uid", 0) or 0)
                if room_lich_uid > 0 and _room_remaining_slots(self.server, room_lich_uid) > 0 and _room_forage_candidates(self.server, room):
                    forage_candidates.append(int(room_id))

        return {
            "room_synth_counts": room_synth_counts,
            "room_player_counts": room_player_counts,
            "room_safe": room_safe,
            "hunt_candidates": hunt_candidates,
            "forage_candidates": forage_candidates,
        }

    def _collect_finished_plans(self):
        finished = []
        for actor_id, future in list(self._planner_futures.items()):
            if not future.done():
                continue
            finished.append((actor_id, future))
        for actor_id, future in finished:
            self._planner_futures.pop(actor_id, None)
            self._perf["planner_done"] += 1
            actor = self._actors.get(actor_id)
            if not actor:
                continue
            try:
                actor.synthetic_flags["planned_action"] = dict(future.result() or {})
            except Exception:
                log.exception("Fake player planner failed for actor %s", actor_id)

    def _build_roam_candidates(self, actor: SyntheticPlayer, bubble_rooms: set[int], tick_context: dict) -> list[dict]:
        room = getattr(actor, "current_room", None)
        current_room_id = int(getattr(room, "id", 0) or 0)
        hotspot_rooms = self._region_rooms(actor.home_region_key, "hotspot_room_ids")
        rest_rooms = self._region_rooms(actor.home_region_key, "rest_room_ids")
        crafting_rooms = self._region_rooms(actor.home_region_key, "crafting_room_ids")
        travel_rooms = self._region_rooms(actor.home_region_key, "travel_room_ids")
        preferred_rooms = {rid for rid in (hotspot_rooms | rest_rooms | crafting_rooms) if rid in bubble_rooms and rid != current_room_id}
        travel_candidates = {rid for rid in travel_rooms if rid in bubble_rooms and rid != current_room_id}
        candidate_rooms = preferred_rooms or travel_candidates
        if not candidate_rooms:
            return []
        travel_weight = max(0.0, min(1.0, float(self._defaults.get("travel_roam_weight") or 0.18)))
        soft_cap = max(1, int(self._defaults.get("spawn_room_soft_cap") or 3))
        rows = []
        room_counts = dict(tick_context.get("room_synth_counts") or {})
        for candidate_room_id in sorted(candidate_rooms):
            weight = 1.0
            if candidate_room_id in hotspot_rooms:
                weight += 2.2
            if candidate_room_id in rest_rooms:
                weight += 1.3
            if candidate_room_id in crafting_rooms:
                weight += 0.8
            if candidate_room_id in travel_rooms:
                weight *= travel_weight
            occupancy = int(room_counts.get(candidate_room_id, 0))
            if occupancy >= soft_cap:
                weight *= max(0.06, 0.28 / float((occupancy - soft_cap) + 1))
            elif occupancy > 0:
                weight *= max(0.40, 1.0 - (0.14 * occupancy))
            rows.append({"room_id": int(candidate_room_id), "weight": weight})
        return rows

    def _submit_plan(self, actor: SyntheticPlayer, bubble_rooms: set[int], active_case: dict | None, now: float, tick_context: dict) -> bool:
        if not self._planner_pool or actor.synthetic_id in self._planner_futures:
            return False
        if len(self._planner_futures) >= self._plan_queue_limit():
            return False
        room = getattr(actor, "current_room", None)
        room_id = int(getattr(room, "id", 0) or getattr(actor, "current_room_id", 0) or 0)
        stay = self.server.inns.get_stay(actor.character_id) if getattr(self.server, "inns", None) else None
        room_counts = dict(tick_context.get("room_synth_counts") or {})
        player_counts = dict(tick_context.get("room_player_counts") or {})
        hunt_candidates = []
        if room_id > 0 and room_id in bubble_rooms and self.server.creatures.get_creatures_in_room(room_id):
            creature_levels = [int(getattr(c, "level", actor.level) or actor.level) for c in self.server.creatures.get_creatures_in_room(room_id) if getattr(c, "alive", False)]
            if creature_levels:
                hunt_candidates.append({
                    "room_id": room_id,
                    "min_level": min(creature_levels),
                    "max_level": max(creature_levels),
                })
        hunt_candidates.extend(list(tick_context.get("hunt_candidates") or []))
        normalized_hunt = []
        seen_hunt = set()
        for row in hunt_candidates:
            room_candidate_id = int(row.get("room_id") or 0)
            if room_candidate_id <= 0 or room_candidate_id in seen_hunt:
                continue
            seen_hunt.add(room_candidate_id)
            min_level = int(row.get("min_level") or actor.level)
            max_level = int(row.get("max_level") or min_level)
            gap = min(abs(min_level - actor.level), abs(max_level - actor.level))
            normalized_hunt.append({"room_id": room_candidate_id, "gap": gap})
        payload = {
            "seed": int((now * 1000) + actor.synthetic_id),
            "has_room": bool(room),
            "blocked_status": str((active_case or {}).get("status") or "") in {"incarcerated", "service", "awaiting_sentence"},
            "room_safe": bool(getattr(room, "safe", False)) if room else False,
            "current_room_id": room_id,
            "occupants": max(0, int(room_counts.get(room_id, 0) + player_counts.get(room_id, 0) - 1)),
            "synthetic_count": max(0, int(room_counts.get(room_id, 0))),
            "real_player_present": int(player_counts.get(room_id, 0)) > 0,
            "social_bias": float(self._personality(actor, "social", 0.25)),
            "rude_bias": float(self._personality(actor, "rude", 0.12)),
            "craft_bias": float(self._personality(actor, "craft", 0.15)),
            "roam_bias": float(self._personality(actor, "roam", 0.20)),
            "hunt_bias": float(self._personality(actor, "hunt", 0.18)),
            "crime_bias": float(self._personality(actor, "crime", 0.03)),
            "inn_bias": float(self._archetype_bias(actor, "inn_bias", 0.10)),
            "idle_bias": float(self._archetype_bias(actor, "idle_bias", 0.55)),
            "pawn_bias": float(self._archetype_bias(actor, "pawn_bias", 0.10)),
            "locksmith_bias": float(self._archetype_bias(actor, "locksmith_bias", 0.10)),
            "safe_room_suppression": float(self._defaults.get("safe_room_task_suppression") or 0.34),
            "spill_threshold": int(self._defaults.get("safe_room_crowd_spill_threshold") or 4),
            "spill_chance": float(self._defaults.get("safe_room_crowd_spill_chance") or 0.78),
            "safe_room_linger_base": float(self._defaults.get("safe_room_linger_base") or 0.18),
            "safe_room_social_min_delay": float(self._defaults.get("safe_room_social_min_delay") or 2),
            "safe_room_social_max_delay": float(self._defaults.get("safe_room_social_max_delay") or 5),
            "town_afk_emote_chance": float(self._defaults.get("town_afk_emote_chance") or 0.24),
            "service_task_chance_safe": float(self._defaults.get("service_task_chance_safe") or 0.20),
            "can_service": bool(getattr(room, "safe", False)),
            "can_locksmith_customer": bool(room and room.id in self._service_rooms["locksmith"] and any(str(item.get("item_type") or "").lower() == "container" and item.get("is_locked", True) for item in list(actor.inventory or []))),
            "can_locksmith_rogue": bool(room and room.id in self._service_rooms["locksmith"] and (int(actor.profession_id or 0) == 2 or "rogue" in actor.profession.lower())),
            "can_pawn": bool(room and room.id in self._service_rooms["pawn"] and any(str(item.get("item_type") or "").lower() in {"gem", "scroll", "herb", "misc", "weapon", "armor"} for item in list(actor.inventory or []))),
            "can_inn": bool(getattr(self.server, "inns", None)),
            "has_inn_stay": bool(stay),
            "at_inn_front_desk": bool(room and room.id in self._service_rooms["inn"]),
            "can_lawbreak": bool(room),
            "can_hunt": True,
            "can_forage": True,
            "hunt_candidates": normalized_hunt,
            "forage_candidates": list(tick_context.get("forage_candidates") or []),
            "roam_candidates": self._build_roam_candidates(actor, bubble_rooms, tick_context),
        }
        future = self._planner_pool.submit(plan_actor_action, payload)
        self._planner_futures[actor.synthetic_id] = future
        self._perf["planner_submit"] += 1
        return True

    async def _execute_planned_action(self, actor: SyntheticPlayer, plan: dict, bubble_rooms: set[int], anchors: list[int], active_case: dict | None, now: float) -> bool:
        action = str((plan or {}).get("action") or "").strip().lower()
        target_room_id = int((plan or {}).get("target_room_id") or 0)
        if action == "spawn":
            room_id = self._pick_spawn_room(bubble_rooms, anchors)
            if room_id > 0:
                self._place_actor(actor, room_id)
            return True
        if action == "social":
            return await self._maybe_socialize(actor)
        if action == "afk_emote":
            actor.position = random.choice(["standing", "sitting", "resting"])
            await self._emote(actor, random.choice([
                "idles near the wall and watches the room drift around them.",
                "looks half-afk for a moment, then refocuses on the room.",
                "settles in like they plan to stay a while and let the gossip come to them.",
                "checks their gear, then goes still and listens to the room.",
                "leans back and lets the crowd noise do the work for a while.",
            ]))
            return True
        if action == "locksmith_customer":
            return bool(self._maybe_locksmith_customer(actor))
        if action == "locksmith_rogue":
            return bool(self._maybe_locksmith_rogue(actor))
        if action == "pawn":
            return bool(self._maybe_pawn(actor))
        if action == "inn":
            return await self._maybe_inn_cycle(actor, now)
        if action == "lawbreak":
            return await self._maybe_lawbreaking(actor, active_case)
        if action == "hunt_here":
            return await self._maybe_hunt(actor, bubble_rooms)
        if action == "hunt_move" and target_room_id > 0:
            room = getattr(actor, "current_room", None)
            if room and getattr(room, "safe", False):
                await self._maybe_announce_hunt_party(actor, target_room_id)
            return await self._move_toward(actor, target_room_id)
        if action == "forage_here":
            return await self._maybe_forage(actor, bubble_rooms)
        if action == "forage_move" and target_room_id > 0:
            await self._maybe_announce_forage_trip(actor)
            return await self._move_toward(actor, target_room_id)
        if action == "craft":
            return await self._maybe_fake_craft(actor)
        if action == "roam" and target_room_id > 0:
            room = getattr(actor, "current_room", None)
            if room and getattr(room, "safe", False) and self._room_occupants_except(actor):
                if random.random() < 0.24:
                    await self._maybe_announce_quest_help(actor, target_room_id)
            return await self._move_toward(actor, target_room_id)
        if action == "wait":
            return True
        return await self._choose_action(actor, bubble_rooms, anchors, active_case, now)

    async def _combat_tick(self, actor: SyntheticPlayer, now: float):
        target = getattr(actor, "target", None)
        if actor.get_roundtime() > 0:
            return
        if not target or not getattr(target, "alive", False):
            actor.in_combat = False
            actor.target = None
            return
        killed = await self.server.combat.player_attacks_creature(actor, target)
        actor.synthetic_flags["next_action_at"] = now + random.uniform(2.5, 5.0)
        if killed:
            actor.in_combat = False
            actor.target = None
            actor.field_experience += int(self._defaults.get("hunt_field_xp_gain") or 140)
            self._award_loot(actor, target)

    def _award_loot(self, actor: SyntheticPlayer, creature):
        level = int(getattr(creature, "level", actor.level) or actor.level)
        if random.random() < 0.55:
            box = generate_box(getattr(self.server, "db", None), level, server=self.server)
            if box:
                actor.inventory.append(box)
        if random.random() < 0.45:
            gem = generate_gem(getattr(self.server, "db", None), level)
            if gem:
                actor.inventory.append(gem)
        if random.random() < 0.18:
            scroll = generate_scroll(getattr(self.server, "db", None), level)
            if scroll:
                actor.inventory.append(scroll)
        actor.silver += random.randint(level * 8, max(level * 15, 20))

    def _active_argument(self, room_id: int) -> dict | None:
        room_id = int(room_id or 0)
        if room_id <= 0:
            return None
        thread = self._room_arguments.get(room_id)
        if not thread:
            return None
        if float(thread.get("expires_at") or 0.0) <= _now():
            self._room_arguments.pop(room_id, None)
            return None
        return thread

    def _active_conversation(self, room_id: int) -> dict | None:
        room_id = int(room_id or 0)
        if room_id <= 0:
            return None
        thread = self._room_conversations.get(room_id)
        if not thread:
            return None
        if float(thread.get("expires_at") or 0.0) <= _now():
            self._room_conversations.pop(room_id, None)
            return None
        return thread

    def _conversation_topics_for(self, actor: SyntheticPlayer) -> list[tuple[str, str, str]]:
        low_silver = int(getattr(actor, "silver", 0) or 0) < max(150, actor.level * 35)
        has_hunt_loot = any(str(item.get("item_type") or "").lower() in {"container", "gem", "scroll"} for item in list(getattr(actor, "inventory", []) or []))
        profession = str(getattr(actor, "profession", "") or "").lower()
        topics = [
            ("money_talk", "money_reply", "I could use a cleaner silver route than the one I've got."),
            ("boss_talk", "boss_reply", "Most people still miss the weak point even when it's right in front of them."),
            ("hunt_talk", "hunt_reply", "People keep choosing ugly hunting routes and calling it bravery."),
            ("pawn_talk", "pawn_reply", "The pawn counter keeps eating silver from people who should know better."),
            ("locksmith_talk", "locksmith_reply", "Most of the locksmith game is patience and not being a moron."),
            ("training_talk", "training_reply", "Too many builds are made for arguments instead of actual play."),
            ("spell_talk", "spell_reply", "Casters keep confusing noise with good spell use."),
            ("gear_talk", "gear_reply", "A clean kit you understand beats expensive nonsense every time."),
            ("justice_talk", "justice_reply", "Most trouble with the watch starts with someone needing an audience."),
            ("travel_talk", "travel_reply", "Bad routing wastes more nights than bad luck does."),
            ("death_talk", "death_reply", "People talk about dying like the bill stops at pride."),
            ("inn_talk", "inn_reply", "Good rest fixes more plans than one more reckless outing."),
            ("forage_talk", "forage_reply", "People sneer at foraging right up until it pays their herb bill."),
            ("encumbrance_talk", "encumbrance_reply", "Half the square is carrying enough junk to lose a fight before it starts."),
            ("pet_talk", "pet_reply", "A calm companion says more about someone than most speeches do."),
            ("direct_friendly", "direct_reply_friendly", "This room finally feels alive for once."),
        ]
        weighted = []
        for talk_key, reply_key, fallback in topics:
            weight = 1.0
            if low_silver and talk_key in {"money_talk", "pawn_talk", "locksmith_talk", "forage_talk"}:
                weight += 2.0
            if has_hunt_loot and talk_key in {"boss_talk", "hunt_talk", "gear_talk", "death_talk"}:
                weight += 1.5
            if profession in {"rogue"} and talk_key in {"locksmith_talk", "encumbrance_talk", "money_talk"}:
                weight += 1.2
            if profession in {"wizard", "sorcerer", "cleric", "empath"} and talk_key in {"spell_talk", "boss_talk", "gear_talk"}:
                weight += 1.2
            if profession in {"ranger"} and talk_key in {"forage_talk", "travel_talk", "hunt_talk"}:
                weight += 1.2
            if profession in {"bard"} and talk_key in {"inn_talk", "gear_talk", "money_talk"}:
                weight += 1.0
            if profession in {"monk", "paladin", "warrior"} and talk_key in {"training_talk", "gear_talk", "death_talk"}:
                weight += 1.0
            weighted.append((talk_key, reply_key, fallback, weight))
        random.shuffle(weighted)
        weighted.sort(key=lambda row: random.random() * row[3], reverse=True)
        return [(talk_key, reply_key, fallback) for talk_key, reply_key, fallback, _ in weighted]

    async def _emit_conversation_turn(self, actor: SyntheticPlayer, target, thread: dict, use_reply: bool) -> bool:
        room = getattr(actor, "current_room", None)
        if not room or getattr(target, "current_room", None) is not room:
            return False
        tokens = {"target": getattr(target, "character_name", "you"), "player": getattr(target, "character_name", "you")}
        key = str(thread.get("reply_key") if use_reply else thread.get("talk_key") or "")
        fallback = str(thread.get("fallback") or f"{tokens['target']}, that's the shape of it.")
        text = self._pick_dialogue(key, fallback, actor=actor, tokens=tokens)
        await self._say(actor, text)
        thread["turns"] = int(thread.get("turns") or 0) + 1
        thread["last_speaker_id"] = actor.synthetic_id
        thread["next_speaker_id"] = int(getattr(target, "synthetic_id", 0) or 0)
        thread["next_turn_at"] = _now() + random.uniform(
            float(self._defaults.get("conversation_reply_min_seconds") or 12),
            float(self._defaults.get("conversation_reply_max_seconds") or 30),
        )
        self._room_conversations[int(room.id)] = thread
        self._set_pair_cooldown(actor, target, seconds=18.0)
        return True

    async def _maybe_continue_conversation(self, actor: SyntheticPlayer, occupants: list) -> bool:
        room = getattr(actor, "current_room", None)
        thread = self._active_conversation(getattr(room, "id", 0))
        if not room or not thread:
            return False
        if int(thread.get("next_speaker_id") or 0) not in {0, actor.synthetic_id}:
            return False
        if _now() < float(thread.get("next_turn_at") or 0.0):
            return False
        target_id = int(thread.get("last_speaker_id") or 0)
        target = next((p for p in occupants if int(getattr(p, "synthetic_id", 0) or 0) == target_id), None)
        if not target or not getattr(target, "is_synthetic_player", False):
            self._room_conversations.pop(int(room.id), None)
            return False
        use_reply = bool(int(thread.get("turns") or 0) % 2 == 0)
        if int(thread.get("turns") or 0) >= 6:
            self._room_conversations.pop(int(room.id), None)
            return False
        return await self._emit_conversation_turn(actor, target, thread, use_reply=use_reply)

    async def _maybe_start_conversation(self, actor: SyntheticPlayer, occupants: list) -> bool:
        room = getattr(actor, "current_room", None)
        if not room or self._active_conversation(room.id) or self._active_argument(room.id):
            return False
        target = next((p for p in occupants if getattr(p, "is_synthetic_player", False) and self._pair_ready(actor, p)), None)
        if not target:
            return False
        if random.random() > max(0.18, float(self._personality(actor, "social", 0.25)) * 0.9):
            return False
        for talk_key, reply_key, fallback in self._conversation_topics_for(actor):
            thread = {
                "talk_key": talk_key,
                "reply_key": reply_key,
                "fallback": fallback,
                "expires_at": _now() + float(self._defaults.get("conversation_thread_seconds") or 420),
                "turns": 0,
                "last_speaker_id": 0,
                "next_speaker_id": actor.synthetic_id,
                "next_turn_at": _now(),
            }
            self._room_conversations[int(room.id)] = thread
            if await self._emit_conversation_turn(actor, target, thread, use_reply=False):
                return True
        return False

    async def _emit_argument_turn(self, actor: SyntheticPlayer, target, thread: dict, stage_key: str) -> bool:
        room = getattr(actor, "current_room", None)
        if not room or getattr(target, "current_room", None) is not room:
            return False
        topic = dict(self._argument_topics.get(str(thread.get("topic") or "")) or {})
        if not topic:
            return False
        tokens = {"target": getattr(target, "character_name", "you"), "player": getattr(target, "character_name", "you")}
        mode = "say"
        if stage_key == "emotes":
            line = self._pick_dialogue("direct_emotes_hostile", f"steps up to {tokens['target']} with a hard stare.", actor=actor, tokens=tokens)
            await self._emote(actor, line)
            mode = "emote"
        else:
            line = self._pick_dialogue(f"argument::{thread.get('topic')}::{stage_key}", "", actor=actor, tokens=tokens)
            if not line:
                rows = list(topic.get(stage_key) or [])
                line = self._pick_dialogue("_unused_argument_fallback", random.choice(rows) if rows else f"{tokens['target']}, this conversation is getting ugly.", actor=actor, tokens=tokens)
            if stage_key == "yells":
                await self._yell(actor, line)
                mode = "yell"
            else:
                await self._say(actor, line)
        now = _now()
        thread["turns"] = int(thread.get("turns") or 0) + 1
        thread["last_speaker_id"] = actor.synthetic_id
        thread["next_speaker_id"] = int(getattr(target, "synthetic_id", 0) or 0)
        thread["next_turn_at"] = now + random.uniform(
            float(self._defaults.get("argument_reply_min_seconds") or 15),
            float(self._defaults.get("argument_reply_max_seconds") or 45),
        )
        self._room_arguments[int(room.id)] = thread
        self._set_pair_cooldown(actor, target, seconds=22.0 if mode == "emote" else 12.0)
        return True

    async def _maybe_continue_argument(self, actor: SyntheticPlayer, occupants: list) -> bool:
        room = getattr(actor, "current_room", None)
        thread = self._active_argument(getattr(room, "id", 0))
        if not room or not thread:
            return False
        if int(thread.get("next_speaker_id") or 0) not in {0, actor.synthetic_id}:
            return False
        if _now() < float(thread.get("next_turn_at") or 0.0):
            return False
        target_id = int(thread.get("last_speaker_id") or 0)
        target = next((p for p in occupants if int(getattr(p, "synthetic_id", 0) or 0) == target_id), None)
        if not target or not getattr(target, "is_synthetic_player", False):
            self._room_arguments.pop(int(room.id), None)
            return False
        turns = int(thread.get("turns") or 0)
        if turns >= 14:
            stage_key = "yells" if random.random() < 0.55 else "emotes"
        elif turns >= 8:
            stage_key = random.choice(["replies", "escalations", "emotes"])
        elif turns >= 3:
            stage_key = random.choice(["replies", "escalations"])
        else:
            stage_key = "replies"
        return await self._emit_argument_turn(actor, target, thread, stage_key)

    async def _maybe_start_argument(self, actor: SyntheticPlayer, occupants: list) -> bool:
        room = getattr(actor, "current_room", None)
        if not room or self._active_argument(room.id):
            return False
        target = next((p for p in occupants if getattr(p, "is_synthetic_player", False) and self._pair_ready(actor, p)), None)
        if not target:
            return False
        if random.random() > max(0.08, float(self._personality(actor, "rude", 0.18)) * 0.9):
            return False
        topic_keys = [str(key) for key, value in self._argument_topics.items() if value]
        if not topic_keys:
            return False
        topic_key = random.choice(topic_keys)
        thread = {
            "topic": topic_key,
            "expires_at": _now() + float(self._defaults.get("argument_thread_seconds") or 900),
            "turns": 0,
            "last_speaker_id": 0,
            "next_speaker_id": actor.synthetic_id,
            "next_turn_at": _now(),
        }
        self._room_arguments[int(room.id)] = thread
        return await self._emit_argument_turn(actor, target, thread, "openers")

    async def _maybe_direct_exchange(self, actor: SyntheticPlayer, occupants: list) -> bool:
        if not occupants:
            return False
        target = random.choice(list(occupants))
        if not self._pair_ready(actor, target):
            return False
        target_name = getattr(target, "character_name", getattr(target, "display_name", "there"))
        rude = random.random() < float(self._personality(actor, "rude", 0.2))
        if rude and random.random() < 0.35:
            await self._emote(actor, self._pick_dialogue("direct_emotes_hostile", f"gives {target_name} a flat, heated look.", actor=actor, tokens={"target": target_name}))
            self._set_pair_cooldown(actor, target, seconds=30.0)
            return True
        if random.random() < 0.22:
            await self._emote(actor, self._pick_dialogue("direct_emotes_friendly", f"gives {target_name} a quick nod.", actor=actor, tokens={"target": target_name}))
            self._set_pair_cooldown(actor, target, seconds=28.0)
            return True
        if rude:
            key = "direct_rude"
            reply_key = "direct_reply_rude"
            fallback = f"{target_name}, you look like you've got something stupid to say."
        else:
            low_silver = int(getattr(actor, "silver", 0) or 0) < max(150, actor.level * 35)
            has_hunt_loot = any(str(item.get("item_type") or "").lower() in {"container", "gem", "scroll"} for item in list(getattr(actor, "inventory", []) or []))
            roll = random.random()
            if low_silver and roll < 0.34:
                key = "money_talk"
                reply_key = "money_reply"
                fallback = f"{target_name}, I could use a clean way to make some silver."
            elif has_hunt_loot and roll < 0.67:
                key = "boss_talk"
                reply_key = "boss_reply"
                fallback = f"{target_name}, most people still miss the weakness right in front of them."
            else:
                key = "hunt_talk"
                reply_key = "hunt_reply"
                fallback = f"{target_name}, people keep choosing ugly hunting routes and acting surprised."
        await self._say(actor, self._pick_dialogue(key, fallback, actor=actor, tokens={"target": target_name, "player": target_name}))
        if getattr(target, "is_synthetic_player", False) and getattr(target, "current_room", None) is getattr(actor, "current_room", None):
            if random.random() < 0.62:
                await self._say(target, self._pick_dialogue(reply_key, f"{actor.character_name}, you're not wrong.", actor=target, tokens={"target": actor.character_name, "player": actor.character_name}))
                self._set_pair_cooldown(actor, target, seconds=45.0)
        else:
            self._set_pair_cooldown(actor, target, seconds=35.0)
        return True

    async def _perform_reaction(self, actor: SyntheticPlayer, reaction: dict) -> bool:
        player_name = str(reaction.get("player_name") or "you")
        direct = bool(reaction.get("direct"))
        message = str(reaction.get("message") or "")
        affinity = int(self._memory_row(actor, int(reaction.get("player_id") or 0)).get("affinity") or 0)
        if reaction.get("kind") == "spam":
            if random.random() < max(0.22, float(self._personality(actor, "rude", 0.2)) * 0.9):
                await self._say(
                    actor,
                    self._pick_dialogue(
                        "spam_callout",
                        f"{player_name}, we heard you the first time. Try silence for variety.",
                        actor=actor,
                        tokens={"target": player_name, "player": player_name},
                    ),
                )
                room = getattr(actor, "current_room", None)
                if room:
                    self._room_prompts[int(room.id)] = {
                        "kind": "spam_callout",
                        "actor_id": actor.synthetic_id,
                        "actor_name": actor.character_name,
                        "tokens": {"target": player_name, "player": player_name},
                        "expires_at": _now() + float(self._defaults.get("intent_prompt_seconds") or 28),
                    }
            else:
                await self._emote(actor, f"winces at {player_name}'s latest burst of noise.")
            return True
        if any(word in message.lower() for word in _INSULT_WORDS) or affinity <= -3:
            if random.random() < float(self._personality(actor, "rude", 0.2)):
                await self._say(actor, self._pick_dialogue("direct_rude", f"{player_name}, learn to breathe through your mouth and spare the rest of us.", actor=actor, tokens={"target": player_name, "player": player_name}))
            else:
                await self._emote(actor, f"gives {player_name} a flat, unimpressed stare.")
            return True
        if direct or any(word in message.lower() for word in _GREETING_WORDS):
            if random.random() < float(self._personality(actor, "shy", 0.1)):
                await self._emote(actor, f"offers {player_name} a hesitant nod.")
            else:
                await self._say(actor, self._pick_dialogue("direct_friendly", f"Well met, {player_name}.", actor=actor, tokens={"target": player_name, "player": player_name}))
            return True
        if reaction.get("kind") == "emote":
            await self._emote(actor, f"mirrors {player_name}'s mood with a faint grin.")
            return True
        return False

    async def _choose_action(self, actor: SyntheticPlayer, bubble_rooms: set[int], anchors: list[int], active_case: dict | None, now: float):
        room = getattr(actor, "current_room", None)
        if not room:
            room_id = self._pick_spawn_room(bubble_rooms, anchors)
            if room_id > 0:
                self._place_actor(actor, room_id)
            actor.synthetic_flags["next_action_at"] = now + random.uniform(2.0, 5.0)
            return
        occupants = self._room_occupants_except(actor)
        safe_room_suppression = min(0.98, float(self._defaults.get("safe_room_task_suppression") or 0.72))
        if getattr(room, "safe", False):
            synthetic_count = 1 + sum(1 for other in occupants if getattr(other, "is_synthetic_player", False))
            spill_threshold = max(2, int(self._defaults.get("safe_room_crowd_spill_threshold") or 4))
            spill_chance = max(0.0, min(1.0, float(self._defaults.get("safe_room_crowd_spill_chance") or 0.78)))
            if synthetic_count >= spill_threshold and random.random() < spill_chance:
                if await self._maybe_roam(actor, bubble_rooms, force=True):
                    actor.synthetic_flags["next_action_at"] = now + random.uniform(4.0, 9.0)
                    return
            social_bias = float(self._personality(actor, "social", 0.25))
            rude_bias = float(self._personality(actor, "rude", 0.12))
            idle_bias = float(self._archetype_bias(actor, "idle_bias", 0.55))
            crowded_bonus = min(0.24, max(0.0, len(occupants)) * 0.06)
            real_player_bonus = 0.22 if any(not getattr(other, "is_synthetic_player", False) for other in occupants) else 0.0
            if random.random() < min(0.92, 0.18 + social_bias * 0.90 + rude_bias * 0.18 + crowded_bonus + real_player_bonus):
                if await self._maybe_socialize(actor):
                    actor.synthetic_flags["next_action_at"] = now + random.uniform(
                        float(self._defaults.get("safe_room_social_min_delay") or 2),
                        float(self._defaults.get("safe_room_social_max_delay") or 6),
                    )
                    return
            linger_roll = float(self._defaults.get("safe_room_linger_base") or 0.58) + (idle_bias * 0.22) + crowded_bonus + real_player_bonus
            if random.random() < min(0.96, linger_roll):
                if random.random() < float(self._defaults.get("town_afk_emote_chance") or 0.38):
                    actor.position = random.choice(["standing", "sitting", "resting"])
                    await self._emote(actor, random.choice([
                        "idles near the wall and watches the room drift around them.",
                        "looks half-afk for a moment, then refocuses on the room.",
                        "settles in like they plan to stay a while and let the gossip come to them.",
                        "checks their gear, then goes still and listens to the room.",
                        "leans back and lets the crowd noise do the work for a while.",
                    ]))
                    actor.synthetic_flags["next_action_at"] = now + random.uniform(2.0, 5.0)
                    return
            if random.random() < safe_room_suppression:
                actor.synthetic_flags["next_action_at"] = now + random.uniform(2.0, 5.5)
                return
        safe_task_gate = 1.0
        if getattr(room, "safe", False):
            safe_task_gate = max(
                0.02,
                float(self._defaults.get("service_task_chance_safe") or 0.20)
                * (0.55 + float(self._archetype_bias(actor, "locksmith_bias", 0.10)) + float(self._archetype_bias(actor, "pawn_bias", 0.10)))
                * (1.0 - safe_room_suppression),
            )
        if random.random() < safe_task_gate and (self._maybe_locksmith_customer(actor) or self._maybe_locksmith_rogue(actor) or self._maybe_pawn(actor)):
            actor.synthetic_flags["next_action_at"] = now + random.uniform(14.0, 24.0)
            return
        if await self._maybe_inn_cycle(actor, now):
            actor.synthetic_flags["next_action_at"] = now + random.uniform(12.0, 26.0)
            return
        if await self._maybe_lawbreaking(actor, active_case):
            actor.synthetic_flags["next_action_at"] = now + random.uniform(20.0, 45.0)
            return
        if await self._maybe_hunt(actor, bubble_rooms):
            actor.synthetic_flags["next_action_at"] = now + random.uniform(6.0, 14.0)
            return
        if await self._maybe_forage(actor, bubble_rooms) or await self._maybe_socialize(actor) or await self._maybe_fake_craft(actor) or await self._maybe_roam(actor, bubble_rooms):
            actor.synthetic_flags["next_action_at"] = now + random.uniform(8.0, 18.0)
            return
        actor.synthetic_flags["next_action_at"] = now + random.uniform(6.0, 16.0)

    def _room_occupants_except(self, actor: SyntheticPlayer) -> list:
        room = getattr(actor, "current_room", None)
        if not room:
            return []
        return [p for p in self.server.world.get_players_in_room(room.id) if p is not actor]

    def _synthetic_room_count(self, room_id: int, exclude_actor: SyntheticPlayer | None = None) -> int:
        room_id = int(room_id or 0)
        if room_id <= 0:
            return 0
        count = 0
        for other in self.in_room(room_id):
            if exclude_actor is not None and other is exclude_actor:
                continue
            count += 1
        return count

    def _quest_prompt_tokens(self, actor: SyntheticPlayer, target_room_id: int) -> dict:
        target_room = self.server.world.get_room(int(target_room_id or 0))
        place = getattr(target_room, "name", None) or self._intent_token("quest_places", "the far side of town")
        task = self._intent_token("quest_tasks", "a guild errand")
        return {
            "target": getattr(actor, "character_name", "you"),
            "player": getattr(actor, "character_name", "you"),
            "place": str(place),
            "task": str(task),
        }

    async def _maybe_announce_hunt_party(self, actor: SyntheticPlayer, target_room_id: int) -> bool:
        room = getattr(actor, "current_room", None)
        if not room or not getattr(room, "safe", False):
            return False
        if not self._intent_ready(actor, "hunt_party"):
            return False
        if random.random() > self._voice_intent_chance(actor, base=0.34):
            return False
        goal = self._intent_token("hunt_goals", "a clean hunt")
        channel = "yell" if len(self._room_occupants_except(actor)) < 1 and random.random() < 0.45 else "say"
        if not await self._announce_room_prompt(
            actor,
            "hunt_party",
            "hunt_party_ask",
            "If anyone's up for a clean hunt, speak now.",
            tokens={"goal": goal},
            channel=channel,
        ):
            return False
        self._stamp_intent(actor, "hunt_party")
        return True

    async def _maybe_announce_forage_trip(self, actor: SyntheticPlayer) -> bool:
        if not self._intent_ready(actor, "forage_trip"):
            return False
        if random.random() > self._voice_intent_chance(actor, base=0.28):
            return False
        need = self._intent_token("forage_needs", "a few decent herbs")
        if not await self._announce_room_prompt(
            actor,
            "forage_departure",
            "forage_departure",
            "I'm going out to pull a few decent herbs before the paths get trampled.",
            tokens={"need": need},
        ):
            return False
        self._stamp_intent(actor, "forage_trip")
        return True

    async def _maybe_announce_quest_help(self, actor: SyntheticPlayer, target_room_id: int) -> bool:
        room = getattr(actor, "current_room", None)
        if not room or not getattr(room, "safe", False):
            return False
        if not self._intent_ready(actor, "quest_help"):
            return False
        if random.random() > self._voice_intent_chance(actor, base=0.24):
            return False
        tokens = self._quest_prompt_tokens(actor, target_room_id)
        if not await self._announce_room_prompt(
            actor,
            "quest_help",
            "quest_help_ask",
            "Anybody know the clean way to handle this errand before I waste half the night on it?",
            tokens=tokens,
        ):
            return False
        self._stamp_intent(actor, "quest_help", seconds=float(self._defaults.get("intent_announce_cooldown_seconds") or 240) * 1.2)
        return True

    async def _maybe_announce_locksmith_customer(self, actor: SyntheticPlayer) -> bool:
        if not self._intent_ready(actor, "locksmith_customer"):
            return False
        if random.random() > self._voice_intent_chance(actor, base=0.30):
            return False
        if not await self._announce_room_prompt(
            actor,
            "locksmith_customer",
            "locksmith_customer_ask",
            "I've got a box that looks mean and I'd rather pay skill than wear the trap.",
        ):
            return False
        self._stamp_intent(actor, "locksmith_customer")
        return True

    async def _maybe_announce_locksmith_warning(self, actor: SyntheticPlayer) -> bool:
        if not self._intent_ready(actor, "locksmith_warning"):
            return False
        if random.random() > self._voice_intent_chance(actor, base=0.42):
            return False
        if not await self._announce_room_prompt(
            actor,
            "locksmith_warning",
            "locksmith_warning",
            "Back up off the bench. This one looks eager to teach a lesson.",
        ):
            return False
        self._stamp_intent(actor, "locksmith_warning", seconds=180.0)
        return True

    async def _maybe_socialize(self, actor: SyntheticPlayer) -> bool:
        room = getattr(actor, "current_room", None)
        if not room:
            return False
        occupants = [p for p in self.server.world.get_players_in_room(room.id) if p is not actor]
        if await self._maybe_continue_argument(actor, occupants):
            return True
        if await self._maybe_continue_conversation(actor, occupants):
            return True
        if await self._maybe_answer_room_prompt(actor, occupants):
            return True
        if random.random() > float(self._personality(actor, "social", 0.25)):
            return False
        if not occupants and random.random() < 0.5:
            return False
        if await self._maybe_start_argument(actor, occupants):
            return True
        if await self._maybe_start_conversation(actor, occupants):
            return True
        roll = random.random()
        if occupants and roll < 0.42:
            return await self._maybe_direct_exchange(actor, occupants)
        if roll < 0.62:
            line_key = "friendly" if random.random() > float(self._personality(actor, "rude", 0.2)) else "rude"
            await self._say(actor, self._pick_dialogue(line_key, "Anyone else feel the square getting louder by the hour?", actor=actor))
        elif roll < 0.82:
            await self._emote(actor, random.choice([
                "glances over the crowd as if measuring the room.",
                "leans against the nearest wall and watches the foot traffic.",
                "checks a belt pouch, then relaxes again.",
            ]))
        elif roll < 0.93:
            await self._yell(actor, self._pick_dialogue("boast", "If anyone sees a decent hunt, point me that way!", actor=actor))
        else:
            await self._shout(actor, self._pick_dialogue("shouts", "If the inn runs out of rooms again, I was here first!", actor=actor))
        return True

    async def _maybe_fake_craft(self, actor: SyntheticPlayer) -> bool:
        room = getattr(actor, "current_room", None)
        if not room or random.random() > float(self._personality(actor, "craft", 0.15)):
            return False
        crafting_rooms = self._region_rooms(actor.home_region_key, "crafting_room_ids")
        if room.id not in crafting_rooms:
            target_room = self._nearest_known_room(room.id, crafting_rooms)
            if target_room > 0:
                await self._move_toward(actor, target_room)
                return True
            return False
        await self._say(actor, self._pick_dialogue("crafting_say", "sorts through a pouch of supplies and mutters about poor grain in the last batch.", actor=actor))
        return True

    async def _maybe_roam(self, actor: SyntheticPlayer, bubble_rooms: set[int], force: bool = False) -> bool:
        room = getattr(actor, "current_room", None)
        if not room:
            return False
        if not force and random.random() > float(self._personality(actor, "roam", 0.20)):
            return False
        hotspot_rooms = self._region_rooms(actor.home_region_key, "hotspot_room_ids")
        rest_rooms = self._region_rooms(actor.home_region_key, "rest_room_ids")
        crafting_rooms = self._region_rooms(actor.home_region_key, "crafting_room_ids")
        travel_rooms = self._region_rooms(actor.home_region_key, "travel_room_ids")
        preferred_rooms = {rid for rid in (hotspot_rooms | rest_rooms | crafting_rooms) if rid in bubble_rooms and rid != room.id}
        travel_candidates = {rid for rid in travel_rooms if rid in bubble_rooms and rid != room.id}
        candidate_rooms = preferred_rooms or travel_candidates
        if not candidate_rooms:
            exits = [int(rid) for rid in (room.exits or {}).values() if int(rid or 0) in bubble_rooms]
            if not exits:
                return False
            await self._move_one_step(actor, random.choice(exits))
            return True
        travel_weight = max(0.0, min(1.0, float(self._defaults.get("travel_roam_weight") or 0.18)))
        soft_cap = max(1, int(self._defaults.get("spawn_room_soft_cap") or 3))
        weighted = []
        for candidate_room_id in sorted(candidate_rooms):
            weight = 1.0
            if candidate_room_id in hotspot_rooms:
                weight += 2.2
            if candidate_room_id in rest_rooms:
                weight += 1.3
            if candidate_room_id in crafting_rooms:
                weight += 0.8
            if candidate_room_id in travel_rooms:
                weight *= travel_weight
            occupancy = self._synthetic_room_count(candidate_room_id)
            if occupancy >= soft_cap:
                weight *= max(0.06, 0.28 / float((occupancy - soft_cap) + 1))
            else:
                weight *= max(0.40, 1.0 - (0.14 * occupancy))
            weighted.append((candidate_room_id, weight))
        target_room = self._weighted_room(weighted) if weighted else 0
        if target_room <= 0:
            return False
        if getattr(room, "safe", False) and self._room_occupants_except(actor):
            if random.random() < 0.24:
                await self._maybe_announce_quest_help(actor, target_room)
        await self._move_toward(actor, target_room)
        return True

    async def _maybe_hunt(self, actor: SyntheticPlayer, bubble_rooms: set[int]) -> bool:
        if random.random() > float(self._personality(actor, "hunt", 0.18)):
            return False
        room = getattr(actor, "current_room", None)
        if not room:
            return False
        creatures_here = [c for c in self.server.creatures.get_creatures_in_room(room.id) if getattr(c, "alive", False)]
        if creatures_here and not getattr(room, "safe", False):
            actor.target = min(creatures_here, key=lambda c: abs(int(getattr(c, "level", actor.level) or actor.level) - actor.level))
            actor.in_combat = True
            await self.server.combat.player_attacks_creature(actor, actor.target)
            return True
        hunt_rooms = []
        for room_id in bubble_rooms:
            room_obj = self.server.world.get_room(room_id)
            if not room_obj or getattr(room_obj, "safe", False):
                continue
            creatures = self.server.creatures.get_creatures_in_room(room_id)
            if not creatures:
                continue
            gap = min(abs(int(getattr(c, "level", actor.level) or actor.level) - actor.level) for c in creatures)
            if gap <= 8:
                hunt_rooms.append((gap, room_id))
        if not hunt_rooms:
            return False
        hunt_rooms.sort(key=lambda row: (row[0], random.random()))
        if getattr(room, "safe", False):
            await self._maybe_announce_hunt_party(actor, hunt_rooms[0][1])
        await self._move_toward(actor, hunt_rooms[0][1])
        return True

    async def _maybe_forage(self, actor: SyntheticPlayer, bubble_rooms: set[int] | None = None) -> bool:
        room = getattr(actor, "current_room", None)
        if not room:
            return False
        if random.random() > max(0.08, float(self._personality(actor, "craft", 0.15)) * 0.55):
            return False
        if getattr(room, "safe", False):
            forage_rooms = []
            for room_id in set(bubble_rooms or set()):
                room_obj = self.server.world.get_room(room_id)
                if not room_obj or getattr(room_obj, "safe", False):
                    continue
                room_lich_uid = int(getattr(room_obj, "lich_uid", 0) or 0)
                if room_lich_uid <= 0:
                    continue
                if _room_remaining_slots(self.server, room_lich_uid) <= 0:
                    continue
                if _room_forage_candidates(self.server, room_obj):
                    forage_rooms.append(int(room_id))
            if not forage_rooms:
                return False
            await self._maybe_announce_forage_trip(actor)
            await self._move_toward(actor, random.choice(sorted(forage_rooms)))
            return True
        if getattr(actor, "right_hand", None) and getattr(actor, "left_hand", None):
            return False
        room_lich_uid = int(getattr(room, "lich_uid", 0) or 0)
        if room_lich_uid <= 0:
            return False
        candidates = _room_forage_candidates(self.server, room)
        if not candidates:
            return False
        if _room_remaining_slots(self.server, room_lich_uid) <= 0:
            return False
        target = _match_requested_candidate("", candidates)
        if not target:
            return False
        hand_attr = _place_in_free_hand_synthetic(actor, target)
        if not hand_attr:
            return False
        _consume_room_slot(self.server, room_lich_uid)
        actor.field_experience += max(5, int(self._defaults.get("idle_field_xp_gain") or 25) // 2)
        await self._emote(actor, "searches the verge carefully and comes up with something useful.")
        return True

    async def _maybe_inn_cycle(self, actor: SyntheticPlayer, now: float) -> bool:
        room = getattr(actor, "current_room", None)
        if not room or not getattr(self.server, "inns", None):
            return False
        stay = self.server.inns.get_stay(actor.character_id)
        if stay and int(stay.get("private_room_id") or 0) == room.id:
            if random.random() < 0.45:
                actor.position = "sleeping"
                actor.field_experience += int(self._defaults.get("sleep_field_xp_gain") or 90)
                await self._emote(actor, "stretches out on the bed and closes their eyes for a while.")
            elif random.random() < 0.35:
                await self.server.inns.latch(actor, True)
                await self._emote(actor, "checks the latch and settles in.")
            else:
                actor.position = "standing"
                exits = self._region_rooms(actor.home_region_key, "hotspot_room_ids") or {actor.home_room_id}
                await self._move_toward(actor, random.choice(sorted(exits)))
            return True
        if stay and int(stay.get("private_table_room_id") or 0) == room.id:
            actor.position = "sitting"
            await self._say(actor, self._pick_dialogue("inn", "This booth's mine for the evening, and I intend to use it properly.", actor=actor))
            return True
        if stay and room.id == int(stay.get("checked_in_room_id") or 0):
            if not int(stay.get("private_room_id") or 0):
                await self.server.inns.check_room(actor)
                return True
            target_room = int(stay.get("private_room_id") or 0)
            if target_room > 0:
                await self._move_toward(actor, target_room)
                return True
        if not stay and random.random() < 0.22:
            if room.id not in self._service_rooms["inn"]:
                target_room = self._nearest_known_room(room.id, self._service_rooms["inn"])
                if target_room > 0:
                    await self._move_toward(actor, target_room)
                    return True
            else:
                await self.server.inns.check_in(actor)
                if random.random() < 0.65:
                    await self.server.inns.check_room(actor)
                return True
        return False

    async def _maybe_lawbreaking(self, actor: SyntheticPlayer, active_case: dict | None) -> bool:
        if active_case:
            return False
        room = getattr(actor, "current_room", None)
        if not room:
            return False
        jurisdiction_id = getattr(self.server.justice, "_resolve_jurisdiction_id", lambda room: None)(room)
        if not jurisdiction_id or random.random() > float(self._personality(actor, "crime", 0.03)):
            return False
        charge_code = random.choice(_LAWBREAKING_CHARGES)
        detail = f"{actor.character_name} caused a disturbance in public."
        if charge_code == "theft":
            detail = f"{actor.character_name} was caught palming a purse they should have left alone."
        elif charge_code == "hooliganism":
            detail = f"{actor.character_name} started yelling abuse and knocking over local property."
        await self._emote(actor, self._pick_dialogue("lawbreaking_minor", "kicks a loose crate and immediately regrets the noise.", actor=actor))
        await self.server.justice.record_crime(actor, jurisdiction_id, charge_code, detail, room_id=room.id)
        await self.server.justice.after_move(actor, room)
        return True

    def _maybe_locksmith_customer(self, actor: SyntheticPlayer) -> bool:
        room = getattr(actor, "current_room", None)
        if not room:
            return False
        boxes = [item for item in list(actor.inventory or []) if str(item.get("item_type") or "").lower() == "container" and item.get("is_locked", True)]
        if not boxes or room.id not in self._service_rooms["locksmith"]:
            return False
        try:
            import asyncio
            asyncio.get_running_loop().create_task(self._maybe_announce_locksmith_customer(actor))
        except Exception:
            log.exception("Failed scheduling locksmith customer banter for %s", actor.character_name)
        item = boxes[0]
        fee = max(50, actor.level * 25)
        job_id = _db_submit(self.server, actor.character_id, actor.character_name, item, fee)
        if not job_id:
            return False
        actor.inventory.remove(item)
        actor.silver = max(0, actor.silver - fee)
        return True

    def _maybe_locksmith_rogue(self, actor: SyntheticPlayer) -> bool:
        room = getattr(actor, "current_room", None)
        if not room or room.id not in self._service_rooms["locksmith"]:
            return False
        if int(actor.profession_id or 0) != 2 and "rogue" not in actor.profession.lower():
            return False
        jobs = _db_get_pending(self.server)
        if not jobs:
            return False
        job = _db_get_job(self.server, int(random.choice(jobs).get("id") or 0))
        if not job or not _db_claim(self.server, int(job["id"]), actor.character_id, actor.character_name, 0):
            return False
        box = _json_loads(job.get("item_data"), {})
        if not isinstance(box, dict) or not box:
            box = {"name": job.get("item_name") or "a box", "short_name": job.get("item_short_name") or "box", "item_type": "container"}
        if box.get("trapped") and not box.get("trap_disarmed"):
            if len(self._room_occupants_except(actor)) > 0:
                try:
                    import asyncio
                    asyncio.get_running_loop().create_task(self._maybe_announce_locksmith_warning(actor))
                except Exception:
                    log.exception("Failed scheduling locksmith warning for %s", actor.character_name)
            trap_fail_roll = random.random()
            rogue_bias = 0.15 if (int(actor.profession_id or 0) == 2 or "rogue" in actor.profession.lower()) else 0.0
            if trap_fail_roll < max(0.12, 0.32 - rogue_bias):
                try:
                    import asyncio
                    loop = asyncio.get_running_loop()
                    loop.create_task(self.server.traps.trigger_trap(actor, box, source="pick"))
                except Exception:
                    log.exception("Failed scheduling synthetic trap trigger for %s", actor.character_name)
                if box.get("trap_type") in {"boomer", "fire_vial", "gas", "spores", "glyph", "sphere"}:
                    actor.synthetic_flags["next_action_at"] = _now() + random.uniform(18.0, 35.0)
                if actor.health_current <= 0 and not actor.is_dead:
                    actor.is_dead = True
                return True
            box["trap_checked"] = True
            box["trap_detected"] = True
            if random.random() < 0.65:
                box["trap_disarmed"] = True
        box["is_locked"] = False
        box["opened"] = False
        box["trap_checked"] = True
        box["trap_detected"] = True
        box["trap_disarmed"] = bool(box.get("trap_disarmed", True))
        return _db_complete(self.server, int(job["id"]), box)

    def _maybe_pawn(self, actor: SyntheticPlayer) -> bool:
        room = getattr(actor, "current_room", None)
        if not room or room.id not in self._service_rooms["pawn"]:
            return False
        shop = _load_shop_by_room(self.server, room.id)
        if not _is_pawn_shop(shop):
            return False
        for item in list(actor.inventory or []):
            if str(item.get("item_type") or "").lower() not in {"gem", "scroll", "herb", "misc", "weapon", "armor"}:
                continue
            _insert_item_into_pawn_backroom(self.server, shop, item, actor.character_name, actor.character_id)
            actor.inventory.remove(item)
            actor.silver += max(1, int(item.get("value") or 0))
            return True
        return False

    async def _move_toward(self, actor: SyntheticPlayer, target_room_id: int) -> bool:
        room = getattr(actor, "current_room", None)
        if not room:
            return False
        path = self._cached_path(room.id, int(target_room_id or 0))
        if len(path) < 2:
            return False
        return await self._move_one_step(actor, int(path[1]))

    async def _move_one_step(self, actor: SyntheticPlayer, next_room_id: int) -> bool:
        room = getattr(actor, "current_room", None)
        if not room:
            return False
        direction = self.server.world.get_direction_between(room.id, next_room_id)
        if getattr(self.server, "inns", None) and not await self.server.inns.before_move(actor, room, next_room_id, direction):
            return False
        if getattr(self.server, "justice", None) and not await self.server.justice.before_move(actor, room, next_room_id, direction):
            return False
        self.server.world.remove_player_from_room(actor, room.id)
        await self.server.world.broadcast_to_room(room.id, f"{actor.character_name} just went {direction}.", exclude=actor)
        new_room = self.server.world.get_room(next_room_id)
        if not new_room:
            self.server.world.add_player_to_room(actor, room.id)
            return False
        actor.previous_room = room
        actor.current_room = new_room
        actor.current_room_id = new_room.id
        actor.position = "standing"
        self.server.world.add_player_to_room(actor, new_room.id)
        await self.server.world.broadcast_to_room(new_room.id, f"{actor.character_name} just arrived.", exclude=actor)
        if getattr(self.server, "justice", None):
            await self.server.justice.after_move(actor, new_room)
        return True

    async def _say(self, actor: SyntheticPlayer, message: str):
        room = getattr(actor, "current_room", None)
        if room and message:
            rendered = self._render_speech(actor.character_name, message)
            if rendered["mode"] == "emote":
                await self.server.world.broadcast_to_room(room.id, f"{actor.character_name} {rendered['text']}", exclude=actor)
                return
            await self.server.world.broadcast_to_room(room.id, rendered["text"], exclude=actor)

    async def _yell(self, actor: SyntheticPlayer, message: str):
        room = getattr(actor, "current_room", None)
        msg = self._projected_message_text(message)
        if not room or not msg:
            return
        room_msg = colorize(f'{actor.character_name} yells, "{msg}"', TextPresets.YELL_LOCAL)
        await self.server.world.broadcast_to_room(room.id, room_msg, exclude=actor)

        one_hop_ids = set()
        for direction, adj_id in (room.exits or {}).items():
            rev = "nearby" if str(direction).startswith("go_") else _OPPOSITES.get(direction, "nearby")
            one_hop_ids.add(adj_id)
            await self.server.world.broadcast_to_room(
                adj_id,
                colorize(f'{actor.character_name} yells from the {rev}, "{msg}"', TextPresets.YELL_NEAR),
            )

        for adj_id in one_hop_ids:
            adj_room = self.server.world.get_room(adj_id)
            if not adj_room:
                continue
            for _, far_id in (adj_room.exits or {}).items():
                if far_id != room.id and far_id not in one_hop_ids:
                    await self.server.world.broadcast_to_room(
                        far_id,
                        colorize(f'You hear a distant yell, "{msg}"', TextPresets.YELL_FAR),
                    )

    async def _shout(self, actor: SyntheticPlayer, message: str):
        room = getattr(actor, "current_room", None)
        msg = self._projected_message_text(message)
        if not room or not msg or not getattr(room, "zone", None):
            return
        local_text = colorize(f'{actor.character_name} shouts, "{msg}"', TextPresets.YELL_LOCAL)
        zone_text = colorize(f'You hear someone shout, "{msg}"', TextPresets.YELL_NEAR)
        for other_room_id in room.zone.rooms:
            text = local_text if other_room_id == room.id else zone_text
            await self.server.world.broadcast_to_room(other_room_id, text, exclude=actor if other_room_id == room.id else None)

    async def _emote(self, actor: SyntheticPlayer, text: str):
        room = getattr(actor, "current_room", None)
        if room and text:
            await self.server.world.broadcast_to_room(room.id, f"{actor.character_name} {text}", exclude=actor)

    def _pick_spawn_room(self, bubble_rooms: set[int], anchors: list[int]) -> int:
        weighted: list[tuple[int, float]] = []
        soft_cap = max(1, int(self._defaults.get("spawn_room_soft_cap") or 3))
        travel_weight = max(0.0, min(1.0, float(self._defaults.get("travel_spawn_weight") or 0.08)))
        region_pool = (
            [self._regions[key] for key in sorted(self._active_region_keys) if key in self._regions]
            if self._active_region_keys
            else list(self._regions.values())
        )
        for region in region_pool:
            region_rooms = set()
            for key in ("hotspot_room_ids", "rest_room_ids", "anchor_room_ids", "travel_room_ids", "crafting_room_ids"):
                region_rooms.update(int(rid) for rid in (region.get(key) or []) if int(rid or 0) > 0)
            hotspot_ids = {int(rid) for rid in (region.get("hotspot_room_ids") or []) if int(rid or 0) > 0}
            rest_ids = {int(rid) for rid in (region.get("rest_room_ids") or []) if int(rid or 0) > 0}
            anchor_ids = {int(rid) for rid in (region.get("anchor_room_ids") or []) if int(rid or 0) > 0}
            travel_ids = {int(rid) for rid in (region.get("travel_room_ids") or []) if int(rid or 0) > 0}
            crafting_ids = {int(rid) for rid in (region.get("crafting_room_ids") or []) if int(rid or 0) > 0}
            for room_id in sorted(region_rooms & bubble_rooms):
                room = self.server.world.get_room(room_id)
                if not room:
                    continue
                weight = 1.0
                if room_id in hotspot_ids:
                    weight += 3.0
                if room_id in rest_ids:
                    weight += 2.0
                if room_id in anchor_ids:
                    weight += 0.45
                if room_id in crafting_ids:
                    weight += 0.75
                if room_id in travel_ids:
                    weight *= travel_weight
                kind = str(region.get("kind") or "").lower()
                if kind == "city":
                    weight += 2.0
                elif kind == "town":
                    weight += 1.0
                if getattr(room, "safe", False):
                    weight += 1.0
                if anchors:
                    dist = self._distance_to_anchor(room_id, anchors)
                    if dist <= 0:
                        weight += 5.5
                    elif dist == 1:
                        weight += 3.4
                    elif dist == 2:
                        weight += 2.2
                    elif dist == 3:
                        weight += 1.4
                    elif dist <= 6:
                        weight += 0.8
                occupancy = self._synthetic_room_count(room_id)
                if occupancy >= soft_cap:
                    weight *= max(0.04, 0.18 / float((occupancy - soft_cap) + 1))
                elif occupancy > 0:
                    weight *= max(0.50, 1.0 - (0.16 * occupancy))
                weighted.append((room_id, weight))
        if not weighted and anchors:
            return int(random.choice(anchors))
        return self._weighted_room(weighted)

    def _nearest_city_region_key(self, room_id: int) -> str:
        room_id = int(room_id or 0)
        if room_id <= 0:
            return ""
        best_key = ""
        best_len = 10**9
        for key, region in self._regions.items():
            if str(region.get("kind") or "").strip().lower() != "city":
                continue
            anchors = [int(rid) for rid in (region.get("anchor_room_ids") or []) if int(rid or 0) > 0]
            if not anchors:
                anchors = [int(rid) for rid in (region.get("hotspot_room_ids") or []) if int(rid or 0) > 0]
            for anchor in anchors:
                distance = self._cached_distance(room_id, anchor)
                if distance < best_len:
                    best_len = distance
                    best_key = key
        return best_key

    def _weighted_room(self, weighted: list[tuple[int, float]]) -> int:
        if not weighted:
            return 0
        total = sum(max(0.0, weight) for _, weight in weighted)
        roll = random.uniform(0.0, total or 1.0)
        upto = 0.0
        for room_id, weight in weighted:
            upto += max(0.0, weight)
            if roll <= upto:
                return int(room_id)
        return int(weighted[-1][0])

    def _nearest_known_room(self, from_room_id: int, candidates: set[int]) -> int:
        best_room = 0
        best_len = 10**9
        for candidate in {int(rid) for rid in candidates if int(rid or 0) > 0}:
            distance = self._cached_distance(int(from_room_id or 0), candidate)
            if 1 <= distance < best_len:
                best_len = distance
                best_room = candidate
        return best_room

    def _region_rooms(self, region_key: str, field: str) -> set[int]:
        region = self._regions.get(str(region_key or "").strip().lower()) or {}
        return {int(rid) for rid in (region.get(field) or []) if int(rid or 0) > 0}

    def _render_speech(self, speaker: str, raw_text: str) -> dict:
        text = str(raw_text or "").strip()
        if not text:
            return {"mode": "empty", "text": ""}
        inline = _INLINE_SPEECH_RE.match(text)
        if inline:
            return {"mode": "emote", "text": text}
        prefixed = _SPEECH_PREFIX_RE.match(text)
        if prefixed:
            verb = str(prefixed.group("verb") or "says").lower()
            message = str(prefixed.group("message") or "").strip()
            if message:
                return {
                    "mode": "speech",
                    "text": f"{colorize(speaker, TextPresets.PLAYER_NAME)} {verb}, {colorize(chr(34) + message + chr(34), TextPresets.SYNTHETIC_SPEECH_QUOTE)}",
                }
        lowered = text.lower()
        if lowered.startswith(_EMOTE_LEADS):
            return {"mode": "emote", "text": text}
        return {
            "mode": "speech",
            "text": f"{colorize(speaker, TextPresets.PLAYER_NAME)} says, {colorize(chr(34) + text + chr(34), TextPresets.SYNTHETIC_SPEECH_QUOTE)}",
        }

    def _projected_message_text(self, raw_text: str) -> str:
        text = str(raw_text or "").strip()
        if not text:
            return ""
        prefixed = _SPEECH_PREFIX_RE.match(text)
        if prefixed:
            return str(prefixed.group("message") or "").strip()
        inline = _INLINE_SPEECH_RE.match(text)
        if inline:
            return str(inline.group("message") or "").strip()
        return text

    def _format_dialogue_text(self, text: str, tokens: dict | None = None) -> str:
        rendered = str(text or "")
        for key, value in dict(tokens or {}).items():
            rendered = rendered.replace("{" + str(key) + "}", str(value))
        return rendered.strip()

    def _cleanup_dialogue_cache(self, actor: SyntheticPlayer | None = None):
        now = _now()
        global_window = max(30, int(self._defaults.get("dialogue_repeat_global_seconds") or 300))
        self._recent_dialogue_global = {
            key: seen_at
            for key, seen_at in self._recent_dialogue_global.items()
            if (now - float(seen_at or 0.0)) <= global_window
        }
        if actor is None:
            return
        actor_window = max(60, int(self._defaults.get("dialogue_repeat_actor_seconds") or 720))
        recent = dict(actor.synthetic_flags.get("recent_dialogue") or {})
        actor.synthetic_flags["recent_dialogue"] = {
            key: seen_at
            for key, seen_at in recent.items()
            if (now - float(seen_at or 0.0)) <= actor_window
        }

    def _dialogue_builder_candidates(self, key: str, tokens: dict | None = None, limit: int = 36) -> list[str]:
        normalized_key = str(key or "").strip()
        if normalized_key in self._dialogue_builder_disabled_keys:
            return []
        builder = dict(self._dialogue_builders.get(normalized_key) or {})
        if not builder:
            return []
        limit = min(max(8, int(limit or 0)), 18)
        groups = []
        for part_key in ("openers", "subjects", "details", "closers"):
            rows = [self._format_dialogue_text(row, tokens) for row in (builder.get(part_key) or []) if str(row or "").strip()]
            if rows:
                groups.append(rows)
        if not groups:
            return []
        candidates = set()
        attempts = 0
        while len(candidates) < limit and attempts < max(24, limit * 6):
            attempts += 1
            parts = [random.choice(group) for group in groups]
            text = " ".join(part for part in parts if part).strip()
            if text:
                candidates.add(text)
        return list(candidates)

    def _remember_dialogue(self, actor: SyntheticPlayer | None, text: str):
        cleaned = str(text or "").strip()
        if not cleaned:
            return
        now = _now()
        self._recent_dialogue_global[cleaned.lower()] = now
        self._dirty_dialogue_global[cleaned.lower()] = now
        if actor is not None:
            recent = dict(actor.synthetic_flags.get("recent_dialogue") or {})
            recent[cleaned.lower()] = now
            actor.synthetic_flags["recent_dialogue"] = recent
        self._cleanup_dialogue_cache(actor)

    def _load_global_dialogue_history(self):
        if not getattr(self.server, "db", None):
            return
        window_seconds = max(60, int(self._defaults.get("dialogue_repeat_global_seconds") or 300))
        cutoff_ts = _now() - float(window_seconds)
        try:
            rows = self._fetch_rows(
                """
                SELECT normalized_text, UNIX_TIMESTAMP(last_used_at) AS last_used_ts
                FROM synthetic_player_dialogue_history
                WHERE last_used_at >= FROM_UNIXTIME(%s)
                """,
                (cutoff_ts,),
            )
        except Exception:
            log.exception("Failed loading synthetic dialogue history")
            return
        self._recent_dialogue_global = {
            str(row.get("normalized_text") or "").strip().lower(): float(row.get("last_used_ts") or 0.0)
            for row in rows
            if str(row.get("normalized_text") or "").strip()
        }

    def _flush_global_dialogue_history(self):
        if not self._dirty_dialogue_global or not getattr(self.server, "db", None):
            return
        conn = self.server.db._get_conn()
        try:
            cur = conn.cursor()
            for normalized_text, seen_at in list(self._dirty_dialogue_global.items()):
                if not normalized_text:
                    continue
                text_hash = hashlib.sha1(normalized_text.encode("utf-8")).hexdigest()
                cur.execute(
                    """
                    INSERT INTO synthetic_player_dialogue_history
                        (text_hash, normalized_text, last_used_at, usage_count)
                    VALUES (%s, %s, FROM_UNIXTIME(%s), 1)
                    ON DUPLICATE KEY UPDATE
                        last_used_at = GREATEST(last_used_at, VALUES(last_used_at)),
                        usage_count = usage_count + 1,
                        updated_at = UTC_TIMESTAMP()
                    """,
                    (text_hash, normalized_text, float(seen_at or _now())),
                )
            window_seconds = max(60, int(self._defaults.get("dialogue_repeat_global_seconds") or 300))
            cutoff_ts = _now() - float(window_seconds)
            cur.execute(
                """
                DELETE FROM synthetic_player_dialogue_history
                WHERE last_used_at < FROM_UNIXTIME(%s)
                """,
                (cutoff_ts,),
            )
            self._dirty_dialogue_global.clear()
        except Exception:
            log.exception("Failed flushing synthetic dialogue history")
        finally:
            conn.close()

    def _pick_dialogue(self, key: str, fallback: str, actor: SyntheticPlayer | None = None, tokens: dict | None = None) -> str:
        self._cleanup_dialogue_cache(actor)
        rendered_fallback = self._format_dialogue_text(fallback, tokens)
        candidates = []
        for row in (self._dialogue.get(key) or []):
            text = self._format_dialogue_text(row, tokens)
            if text:
                candidates.append(text)
        candidates.extend(self._dialogue_builder_candidates(key, tokens=tokens))
        if not candidates:
            if rendered_fallback:
                self._remember_dialogue(actor, rendered_fallback)
            return rendered_fallback
        random.shuffle(candidates)
        recent_global = self._recent_dialogue_global
        recent_actor = dict((actor.synthetic_flags.get("recent_dialogue") or {})) if actor is not None else {}
        for text in candidates:
            lowered = text.lower()
            if lowered in recent_actor or lowered in recent_global:
                continue
            self._remember_dialogue(actor, text)
            return text
        text = random.choice(candidates)
        self._remember_dialogue(actor, text)
        return text

    def _pair_key(self, actor: SyntheticPlayer, other) -> str:
        left = int(getattr(actor, "synthetic_id", getattr(actor, "character_id", 0)) or 0)
        right = int(getattr(other, "synthetic_id", getattr(other, "character_id", 0)) or 0)
        return f"{min(left, right)}:{max(left, right)}"

    def _pair_ready(self, actor: SyntheticPlayer, other) -> bool:
        return _now() >= float(self._pair_social_until.get(self._pair_key(actor, other), 0.0) or 0.0)

    def _set_pair_cooldown(self, actor: SyntheticPlayer, other, seconds: float | None = None):
        wait_for = float(seconds if seconds is not None else (self._defaults.get("dialogue_pair_cooldown_seconds") or 90))
        self._pair_social_until[self._pair_key(actor, other)] = _now() + max(8.0, wait_for)

    def _intent_ready(self, actor: SyntheticPlayer, key: str, seconds: float | None = None) -> bool:
        cooldowns = dict(actor.synthetic_flags.get("intent_cooldowns") or {})
        until = float(cooldowns.get(str(key or ""), 0.0) or 0.0)
        return _now() >= until

    def _stamp_intent(self, actor: SyntheticPlayer, key: str, seconds: float | None = None):
        cooldowns = dict(actor.synthetic_flags.get("intent_cooldowns") or {})
        wait_for = float(seconds if seconds is not None else (self._defaults.get("intent_announce_cooldown_seconds") or 240))
        cooldowns[str(key or "")] = _now() + max(20.0, wait_for)
        actor.synthetic_flags["intent_cooldowns"] = cooldowns

    def _voice_intent_chance(self, actor: SyntheticPlayer, base: float = 0.35) -> float:
        social = float(self._personality(actor, "social", 0.25))
        shy = float(self._personality(actor, "shy", 0.10))
        rude = float(self._personality(actor, "rude", 0.12))
        return max(0.08, min(0.92, base + social * 0.45 + rude * 0.08 - shy * 0.28))

    def _active_room_prompt(self, room_id: int) -> dict | None:
        room_id = int(room_id or 0)
        if room_id <= 0:
            return None
        prompt = self._room_prompts.get(room_id)
        if not prompt:
            return None
        if float(prompt.get("expires_at") or 0.0) <= _now():
            self._room_prompts.pop(room_id, None)
            return None
        return prompt

    def _intent_token(self, key: str, fallback: str) -> str:
        rows = [str(row or "").strip() for row in (self._intent_tokens.get(str(key or "")) or []) if str(row or "").strip()]
        if not rows:
            return str(fallback or "")
        return random.choice(rows)

    def _track_player_chat(self, session, kind: str, message: str) -> dict | None:
        if kind not in {"say", "yell", "shout"}:
            return None
        player_id = int(getattr(session, "character_id", 0) or 0)
        if player_id <= 0:
            return None
        state = dict(self._player_chat_state.get(player_id) or {})
        history = list(state.get("history") or [])
        now = _now()
        window_seconds = max(6, int(self._defaults.get("spam_window_seconds") or 18))
        normalized = self._projected_message_text(message).strip().lower()
        history = [row for row in history if (now - float((row or {}).get("at") or 0.0)) <= window_seconds]
        history.append({"at": now, "kind": str(kind or ""), "text": normalized})
        self._player_chat_state[player_id] = {"history": history}
        repeated = sum(1 for row in history if str(row.get("text") or "") == normalized and normalized)
        total_lines = len(history)
        loud_lines = sum(1 for row in history if str(row.get("kind") or "") in {"yell", "shout"})
        if repeated >= int(self._defaults.get("spam_repeat_threshold") or 2):
            return {"kind": "repeat", "count": repeated, "text": normalized}
        if loud_lines >= int(self._defaults.get("spam_yell_threshold") or 3):
            return {"kind": "loud", "count": loud_lines, "text": normalized}
        if total_lines >= int(self._defaults.get("spam_line_threshold") or 4):
            return {"kind": "flood", "count": total_lines, "text": normalized}
        return None

    async def _announce_room_prompt(
        self,
        actor: SyntheticPlayer,
        kind: str,
        talk_key: str,
        fallback: str,
        *,
        tokens: dict | None = None,
        channel: str = "say",
    ) -> bool:
        room = getattr(actor, "current_room", None)
        if not room:
            return False
        payload = dict(tokens or {})
        text = self._pick_dialogue(talk_key, fallback, actor=actor, tokens=payload)
        if channel == "yell":
            await self._yell(actor, text)
        elif channel == "shout":
            await self._shout(actor, text)
        else:
            await self._say(actor, text)
        self._room_prompts[int(room.id)] = {
            "kind": str(kind or ""),
            "actor_id": actor.synthetic_id,
            "actor_name": actor.character_name,
            "tokens": payload,
            "expires_at": _now() + float(self._defaults.get("intent_prompt_seconds") or 28),
        }
        return True

    def _prompt_reply_spec(self, actor: SyntheticPlayer, prompt: dict) -> tuple[str, str] | None:
        kind = str(prompt.get("kind") or "")
        asker_name = str(prompt.get("actor_name") or "you")
        rude = float(self._personality(actor, "rude", 0.12))
        hunt = float(self._personality(actor, "hunt", 0.18))
        craft = float(self._personality(actor, "craft", 0.10))
        social = float(self._personality(actor, "social", 0.25))
        if kind == "hunt_party":
            if random.random() < max(0.18, rude * 0.7) or hunt < 0.14:
                return ("hunt_party_decline", f"{asker_name}, find someone with less sense.")
            return ("hunt_party_reply", f"{asker_name}, I can spare one clean run.")
        if kind == "forage_departure":
            if random.random() < max(0.12, rude * 0.45):
                return None
            return ("forage_departure_reply", f"{asker_name}, if you find anything worth carrying, bring it back.")
        if kind == "quest_help":
            if random.random() < max(0.22, rude * 0.65):
                return ("quest_help_decline", f"{asker_name}, ask somebody who likes errands.")
            return ("quest_help_reply", f"{asker_name}, start with the obvious desk before you make it complicated.")
        if kind == "locksmith_customer":
            if craft + hunt + social < 0.25 and random.random() < 0.55:
                return None
            return ("locksmith_customer_reply", f"{asker_name}, set it down and stop jostling the bench.")
        if kind == "locksmith_warning":
            if random.random() < 0.18 and rude > 0.18:
                return None
            return ("locksmith_warning_reply", f"{asker_name}, fair enough, I like my eyebrows where they are.")
        if kind == "spam_callout":
            if random.random() < max(0.35, rude * 0.8):
                return None
            return ("spam_callout_reply", f"{asker_name}, the room was thinking it already.")
        return None

    async def _maybe_answer_room_prompt(self, actor: SyntheticPlayer, occupants: list) -> bool:
        room = getattr(actor, "current_room", None)
        prompt = self._active_room_prompt(getattr(room, "id", 0))
        if not room or not prompt:
            return False
        if int(prompt.get("actor_id") or 0) == actor.synthetic_id:
            return False
        origin = next((p for p in occupants if int(getattr(p, "synthetic_id", 0) or 0) == int(prompt.get("actor_id") or 0)), None)
        if origin is not None and not self._pair_ready(actor, origin):
            return False
        if random.random() > self._voice_intent_chance(actor, base=0.26):
            return False
        spec = self._prompt_reply_spec(actor, prompt)
        if not spec:
            return False
        key, fallback = spec
        tokens = dict(prompt.get("tokens") or {})
        tokens["target"] = str(prompt.get("actor_name") or "you")
        tokens["player"] = tokens["target"]
        await self._say(actor, self._pick_dialogue(key, fallback, actor=actor, tokens=tokens))
        if origin is not None:
            self._set_pair_cooldown(actor, origin, seconds=38.0)
        self._room_prompts.pop(int(room.id), None)
        return True

    def _personality(self, actor: SyntheticPlayer, field: str, fallback: float) -> float:
        return float((self._mbti.get(str(actor.mbti or "").upper()) or {}).get(field, fallback) or fallback)

    def _archetype_bias(self, actor: SyntheticPlayer, field: str, fallback: float = 0.0) -> float:
        key = str(getattr(actor, "archetype", "") or "").strip().lower()
        row = next((dict(item or {}) for item in self._archetypes if str((item or {}).get("key") or "").strip().lower() == key), {})
        return float(row.get(field, fallback) or fallback)

    def _ensure_actor_loadout(self, actor: SyntheticPlayer):
        inventory = list(getattr(actor, "inventory", []) or [])
        needs_refresh = not any(i for i in inventory if str(i.get("slot") or "").lower() not in {"", "right_hand", "left_hand"})
        if not needs_refresh and getattr(actor, "right_hand", None):
            return
        built = self._build_loadout(actor.profession, int(actor.level or 1))
        if not built:
            return
        if needs_refresh:
            loose = [i for i in inventory if not i or not i.get("slot")]
            inventory = list(built["inventory"]) + loose
            actor.inventory = inventory
        if not getattr(actor, "right_hand", None) and built.get("right_hand"):
            actor.right_hand = dict(built["right_hand"])
        if not getattr(actor, "left_hand", None) and built.get("left_hand"):
            actor.left_hand = dict(built["left_hand"])
        self._assign_synthetic_inventory_refs(actor)

    def _build_loadout(self, profession_name: str, level: int) -> dict:
        outfits = dict(self._cfg.get("outfits") or {})
        defaults = [dict(row) for row in (outfits.get("defaults") or []) if isinstance(row, dict)]
        profession_outfits = dict((outfits.get("professions") or {})).get(str(profession_name or "").strip().lower(), []) or []
        tier_key, tier_cfg = self._gear_tier(level)
        accent = str((tier_cfg or {}).get("accent_color") or "").strip()
        inventory = []
        for spec in defaults + [dict(row) for row in profession_outfits if isinstance(row, dict)]:
            item = dict(spec)
            item.setdefault("article", "a")
            item.setdefault("slot", item.get("worn_location"))
            item.setdefault("worn_location", item.get("slot"))
            item.setdefault("weight", 1.0)
            item.setdefault("value", 0)
            item.setdefault("synthetic_item", True)
            if accent and item.get("item_type") in {"clothing", "armor", "container"} and not item.get("color"):
                item["color"] = accent
            inventory.append(item)

        prof_key = str(profession_name or "").strip().lower()
        prof_cfg = dict((self._gear.get("professions") or {})).get(prof_key, {}) or {}
        armor = self._template_item_for_tier(prof_cfg.get("armor_by_tier"), tier_key, slot="torso")
        if armor:
            if accent and not armor.get("color"):
                armor["color"] = accent
            inventory = [item for item in inventory if str(item.get("slot") or "").lower() != "torso"]
            inventory.append(armor)

        for container_spec in (prof_cfg.get("container_templates") or []):
            if not isinstance(container_spec, dict):
                continue
            item = self._template_item(str(container_spec.get("template") or ""), slot=str(container_spec.get("slot") or "") or None)
            if not item:
                continue
            item["synthetic_item"] = True
            if accent and not item.get("color"):
                item["color"] = accent
            target_slot = str(item.get("slot") or "").lower()
            if target_slot:
                inventory = [row for row in inventory if str(row.get("slot") or "").lower() != target_slot]
            inventory.append(item)

        shield = self._template_item_for_tier(prof_cfg.get("shield_by_tier"), tier_key, slot="arm")
        if shield:
            shield["synthetic_item"] = True
            inventory = [row for row in inventory if str(row.get("slot") or "").lower() != "arm"]
            inventory.append(shield)

        right_hand = self._template_item_for_tier(prof_cfg.get("weapon_by_tier"), tier_key, slot="right_hand")
        if right_hand:
            right_hand["synthetic_item"] = True
            if accent and not right_hand.get("color"):
                right_hand["color"] = accent

        pocket_items = self._build_pocket_items(prof_cfg, tier_cfg)
        primary_container = next((item for item in inventory if str(item.get("item_type") or "").lower() == "container"), None)
        if pocket_items:
            inventory.extend(pocket_items)

        actor_like = type("LoadoutHolder", (), {})()
        actor_like.inventory = inventory
        actor_like.right_hand = right_hand
        actor_like.left_hand = None
        self._assign_synthetic_inventory_refs(actor_like)
        if primary_container and primary_container.get("inv_id") is not None:
            for item in pocket_items:
                item["container_id"] = primary_container.get("inv_id")
        return {"inventory": actor_like.inventory, "right_hand": actor_like.right_hand, "left_hand": actor_like.left_hand}

    def _gear_tier(self, level: int) -> tuple[str, dict]:
        tiers = dict(self._gear.get("tiers") or {})
        ordered = sorted(
            ((str(key), dict(value or {})) for key, value in tiers.items()),
            key=lambda row: int(row[1].get("max_level") or 999),
        )
        level = int(level or 1)
        for key, cfg in ordered:
            if level <= int(cfg.get("max_level") or 999):
                return key, cfg
        return ("novice", {})

    def _template_item_for_tier(self, tier_map, tier_key: str, slot: str | None = None) -> dict | None:
        if not isinstance(tier_map, dict):
            return None
        choice = tier_map.get(tier_key) or tier_map.get("novice")
        return self._template_item(str(choice or ""), slot=slot)

    def _template_item(self, short_name: str, slot: str | None = None) -> dict | None:
        wanted = str(short_name or "").strip().lower()
        if not wanted:
            return None
        if wanted in {"gem", "gems"}:
            item = generate_gem(getattr(self.server, "db", None), max(1, self._target_level()))
            if item:
                item["synthetic_item"] = True
                if slot:
                    item["slot"] = slot
            return item
        row = self._item_template_cache.get(wanted)
        if wanted not in self._item_template_cache:
            row = self._fetch_item_template(wanted)
            self._item_template_cache[wanted] = row
        if not row:
            return None
        item = dict(row)
        item["inv_id"] = None
        item["container_id"] = None
        item["synthetic_item"] = True
        target_slot = str(slot or row.get("worn_location") or "").strip().lower()
        if target_slot:
            item["slot"] = target_slot
            item.setdefault("worn_location", target_slot)
        return item

    def _fetch_item_template(self, wanted: str) -> dict | None:
        rows = self._fetch_rows(
            """
            SELECT id, name, short_name, noun, article, item_type, material, weapon_type, weapon_category,
                   damage_factor, damage_type, weapon_speed, attack_bonus, damage_bonus, armor_asg, armor_group,
                   defense_bonus, action_penalty, spell_hindrance, shield_size, shield_type, shield_ds,
                   shield_evade_penalty, container_capacity, enchant_bonus, worn_location, weight, value, description
            FROM items
            WHERE is_template = 1 AND (LOWER(short_name) = %s OR LOWER(name) = %s)
            LIMIT 1
            """,
            (wanted, wanted),
        )
        if not rows:
            rows = self._fetch_rows(
                """
                SELECT id, name, short_name, noun, article, item_type, material, weapon_type, weapon_category,
                       damage_factor, damage_type, weapon_speed, attack_bonus, damage_bonus, armor_asg, armor_group,
                       defense_bonus, action_penalty, spell_hindrance, shield_size, shield_type, shield_ds,
                       shield_evade_penalty, container_capacity, enchant_bonus, worn_location, weight, value, description
                FROM items
                WHERE is_template = 1 AND (LOWER(short_name) LIKE %s OR LOWER(name) LIKE %s)
                ORDER BY id ASC
                LIMIT 1
                """,
                (f"%{wanted}%", f"%{wanted}%"),
            )
        if not rows:
            return None
        row = rows[0]
        return {
            "item_id": int(row.get("id") or 0),
            "name": row.get("name"),
            "short_name": row.get("short_name"),
            "noun": row.get("noun"),
            "article": row.get("article") or "a",
            "item_type": row.get("item_type") or "misc",
            "material": row.get("material"),
            "weapon_type": row.get("weapon_type"),
            "weapon_category": row.get("weapon_category") or row.get("weapon_type"),
            "damage_factor": row.get("damage_factor"),
            "damage_type": row.get("damage_type"),
            "weapon_speed": row.get("weapon_speed"),
            "attack_bonus": row.get("attack_bonus") or 0,
            "damage_bonus": row.get("damage_bonus") or 0,
            "armor_asg": row.get("armor_asg"),
            "armor_group": row.get("armor_group"),
            "defense_bonus": row.get("defense_bonus") or 0,
            "action_penalty": row.get("action_penalty") or 0,
            "spell_hindrance": row.get("spell_hindrance") or 0,
            "shield_size": row.get("shield_size") or row.get("shield_type"),
            "shield_type": row.get("shield_type") or row.get("shield_size"),
            "shield_ds": row.get("shield_ds") or 0,
            "shield_evade_penalty": row.get("shield_evade_penalty") or 0,
            "container_capacity": row.get("container_capacity") or 0,
            "enchant_bonus": row.get("enchant_bonus") or 0,
            "worn_location": row.get("worn_location"),
            "weight": row.get("weight") or 1.0,
            "value": row.get("value") or 0,
            "description": row.get("description"),
        }

    def _build_pocket_items(self, prof_cfg: dict, tier_cfg: dict) -> list[dict]:
        templates = list(prof_cfg.get("pocket_templates") or [])
        if not templates:
            return []
        minimum = int((tier_cfg or {}).get("pocket_item_min") or 1)
        maximum = max(minimum, int((tier_cfg or {}).get("pocket_item_max") or minimum))
        count = random.randint(minimum, maximum)
        items = []
        for _ in range(count):
            wanted = str(random.choice(templates) or "").strip()
            item = self._template_item(wanted)
            if not item and wanted.lower() == "gem":
                item = generate_gem(getattr(self.server, "db", None), max(1, self._target_level()))
            if item:
                item["synthetic_item"] = True
                items.append(item)
        return items

    def _assign_synthetic_inventory_refs(self, actor):
        next_ref = -1
        for held in ("right_hand", "left_hand"):
            item = getattr(actor, held, None)
            if isinstance(item, dict) and item.get("inv_id") is None:
                item["inv_id"] = next_ref
                next_ref -= 1
        for item in list(getattr(actor, "inventory", []) or []):
            if not isinstance(item, dict):
                continue
            if item.get("inv_id") is None:
                item["inv_id"] = next_ref
                next_ref -= 1

    def _create_actor_row(self, bubble_rooms: set[int], anchors: list[int]) -> dict | None:
        race = self._weighted_dict(self._races, {"race_id": 1, "name": "Human"})
        profession = self._weighted_dict(self._professions, {"profession_id": 1, "name": "Warrior"})
        archetype = self._weighted_dict(self._archetypes, {"key": "town_regular"})
        mbti = self._weighted_mbti()
        level = self._target_level()
        name = self._unique_name()
        gender = random.choice(["male", "female"])
        room_id = self._pick_spawn_room(bubble_rooms, anchors)
        region_key = self._region_for_room(room_id) or self._closest_region_key(anchors[0] if anchors else room_id)
        stats = self._build_stats(str(profession.get("name") or "warrior"), level)
        skills = self._build_skills(str(profession.get("name") or "warrior"), level)
        loadout = self._build_loadout(str(profession.get("name") or "warrior"), level)
        conn = self.server.db._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO synthetic_players_state
                    (character_id, active, character_name, race_id, race_name, profession_id, profession_name,
                     gender, age, level, level_target, mbti, archetype, home_region_key, home_room_id, current_room_id,
                     health_current, health_max, mana_current, mana_max, spirit_current, spirit_max, stamina_current, stamina_max,
                     silver, experience, field_experience, position, stance, hidden, sneaking, in_combat, is_dead,
                     death_room_id, death_stat_mult, roundtime_end, stat_strength, stat_constitution, stat_dexterity,
                     stat_agility, stat_discipline, stat_aura, stat_logic, stat_intuition, stat_wisdom, stat_influence,
                     inventory_json, right_hand_json, left_hand_json, skills_json, injuries_json, status_effects_json, wounds_json, state_json)
                VALUES
                    (%s, 1, %s, %s, %s, %s, %s,
                     %s, %s, %s, %s, %s, %s, %s, %s, %s,
                     %s, %s, %s, %s, %s, %s, %s, %s,
                     %s, %s, %s, %s, %s, 0, 0, 0, 0,
                     0, 1.0, 0.0, %s, %s, %s,
                     %s, %s, %s, %s, %s, %s, %s,
                     %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    -int(time.time() * 1000) - random.randint(1, 9999),
                    name,
                    int(race.get("race_id") or race.get("id") or 1),
                    str(race.get("name") or "Human"),
                    int(profession.get("profession_id") or profession.get("id") or 1),
                    str(profession.get("name") or "Warrior"),
                    gender,
                    random.randint(19, 72),
                    level,
                    level,
                    mbti,
                    str(archetype.get("key") or "town_regular"),
                    region_key,
                    room_id,
                    room_id,
                    max(35, 85 + level * 8),
                    max(35, 85 + level * 8),
                    max(0, level * 2),
                    max(0, level * 2),
                    10,
                    10,
                    max(70, 80 + level * 3),
                    max(70, 80 + level * 3),
                    random.randint(level * 90, max(level * 180, 200)),
                    level * 2500,
                    random.randint(0, 500),
                    "standing",
                    random.choice(["forward", "neutral", "guarded"]),
                    stats["strength"],
                    stats["constitution"],
                    stats["dexterity"],
                    stats["agility"],
                    stats["discipline"],
                    stats["aura"],
                    stats["logic"],
                    stats["intuition"],
                    stats["wisdom"],
                    stats["influence"],
                    _json_dumps(loadout.get("inventory") or []),
                    _json_dumps(loadout.get("right_hand")),
                    _json_dumps(loadout.get("left_hand")),
                    _json_dumps(skills),
                    "{}",
                    "{}",
                    "{}",
                    _json_dumps({"intent": "idle", "next_action_at": _now() + random.uniform(2.0, 8.0), "memory": {}}),
                ),
            )
            synthetic_id = int(cur.lastrowid or 0)
            cur.execute("UPDATE synthetic_players_state SET character_id = %s WHERE id = %s", (self._justice_id_offset + synthetic_id, synthetic_id))
        finally:
            conn.close()
        return self._fetch_one("SELECT * FROM synthetic_players_state WHERE id = %s", (synthetic_id,))

    def _region_for_room(self, room_id: int) -> str:
        room_id = int(room_id or 0)
        for key, region in self._regions.items():
            for field in ("anchor_room_ids", "hotspot_room_ids", "rest_room_ids", "crafting_room_ids", "travel_room_ids"):
                if room_id in {int(rid) for rid in (region.get(field) or []) if int(rid or 0) > 0}:
                    return key
        return ""

    def _closest_region_key(self, room_id: int) -> str:
        room_id = int(room_id or 0)
        best_key = ""
        best_len = 10**9
        for key, region in self._regions.items():
            for anchor in (region.get("anchor_room_ids") or []):
                distance = self._cached_distance(room_id, int(anchor or 0))
                if distance < best_len:
                    best_len = distance
                    best_key = key
        return best_key or next(iter(self._regions.keys()), "")

    def _weighted_dict(self, rows: list, fallback: dict) -> dict:
        if isinstance(rows, dict):
            normalized = []
            for key, row in rows.items():
                if not isinstance(row, dict):
                    continue
                merged = dict(row)
                merged.setdefault("key", str(key).strip().lower())
                normalized.append(merged)
            rows = normalized
        if not rows:
            return dict(fallback)
        total = sum(max(0.0, float((row or {}).get("weight") or 1.0)) for row in rows)
        roll = random.uniform(0.0, total or 1.0)
        upto = 0.0
        for row in rows:
            upto += max(0.0, float((row or {}).get("weight") or 1.0))
            if roll <= upto:
                return dict(row or {})
        return dict(rows[-1] or fallback)

    def _weighted_mbti(self) -> str:
        return self._weighted_choice([(mbti, float((row or {}).get("weight") or 1.0)) for mbti, row in self._mbti.items()], "ISTJ")

    def _weighted_choice(self, weighted: list[tuple[str, float]], fallback: str) -> str:
        if not weighted:
            return fallback
        total = sum(max(0.0, weight) for _, weight in weighted)
        roll = random.uniform(0.0, total or 1.0)
        upto = 0.0
        for value, weight in weighted:
            upto += max(0.0, weight)
            if roll <= upto:
                return value
        return weighted[-1][0]

    def _target_level(self) -> int:
        sessions = list(getattr(self.server, "sessions", None).playing())
        if not sessions:
            return 8
        avg = sum(int(getattr(s, "level", 1) or 1) for s in sessions) / max(1, len(sessions))
        rules = self._cfg.get("level_rules") or {}
        return _clamp(int(round(avg)) + random.randint(int(rules.get("min_delta") or -5), int(rules.get("max_delta") or 5)), int(rules.get("global_min") or 1), int(rules.get("global_max") or 100))

    def _build_stats(self, profession_name: str, level: int) -> dict:
        prof = profession_name.lower()
        base = 68 + min(20, level // 3)
        stats = {"strength": base, "constitution": base, "dexterity": base, "agility": base, "discipline": base, "aura": base, "logic": base, "intuition": base, "wisdom": base, "influence": base}
        if "warrior" in prof or "paladin" in prof:
            stats["strength"] += 12
            stats["constitution"] += 10
            stats["discipline"] += 6
        elif "rogue" in prof:
            stats["dexterity"] += 12
            stats["agility"] += 12
            stats["intuition"] += 6
        elif "cleric" in prof or "empath" in prof:
            stats["wisdom"] += 12
            stats["aura"] += 10
            stats["intuition"] += 8
        else:
            stats["logic"] += 8
            stats["intuition"] += 8
            stats["discipline"] += 6
        return {key: _clamp(value + random.randint(-4, 4), 45, 100) for key, value in stats.items()}

    def _build_skills(self, profession_name: str, level: int) -> dict:
        prof = profession_name.lower()
        ranks = {4: {"ranks": max(1, level // 2), "bonus": max(5, level * 2)}, 11: {"ranks": max(1, level), "bonus": max(10, level * 5)}, 14: {"ranks": max(1, level), "bonus": max(10, level * 5)}, 2: {"ranks": max(0, level // 2), "bonus": max(0, (level // 2) * 5)}}
        if "rogue" in prof:
            ranks[32] = {"ranks": max(1, level), "bonus": max(10, level * 5)}
            ranks[27] = {"ranks": max(1, level // 2), "bonus": max(5, (level // 2) * 5)}
        if "warrior" in prof or "paladin" in prof:
            ranks[3] = {"ranks": max(0, level // 2), "bonus": max(0, (level // 2) * 5)}
        return ranks

    def _unique_name(self) -> str:
        first_pool = list(self._names.get("first") or ["Mira", "Kerin", "Talin"])
        last_pool = list(self._names.get("last") or ["Vale", "Rook", "Briar"])
        for _ in range(120):
            name = f"{random.choice(first_pool)} {random.choice(last_pool)}"
            if self._name_available(name):
                return name
        return f"{random.choice(first_pool)} {random.randint(100, 999)}"

    def _name_available(self, name: str) -> bool:
        lowered = str(name or "").strip().lower()
        if not lowered:
            return False
        if any(actor.character_name.lower() == lowered for actor in self._actors.values()):
            return False
        if self._fetch_one("SELECT id FROM synthetic_players_state WHERE LOWER(character_name) = %s LIMIT 1", (lowered,)):
            return False
        return not getattr(self.server, "db", None) or not self.server.db.get_character_by_name_basic(name)

    def _fetch_rows(self, sql: str, params=None) -> list[dict]:
        if not getattr(self.server, "db", None):
            return []
        conn = self.server.db._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, params or ())
            return cur.fetchall() or []
        finally:
            conn.close()

    def _fetch_one(self, sql: str, params=None) -> dict | None:
        rows = self._fetch_rows(sql, params)
        return rows[0] if rows else None

    def _execute(self, sql: str, params=None) -> bool:
        if not getattr(self.server, "db", None):
            return False
        normalized = str(sql or "").strip().lower()
        writer = getattr(self.server, "persistence_writer", None)
        if writer and writer.enabled and (
            normalized.startswith("update synthetic_players_state")
            or normalized.startswith("insert into synthetic_player_memory")
            or normalized.startswith("delete from synthetic_player_memory")
            or normalized.startswith("insert into synthetic_player_dialogue_history")
            or normalized.startswith("update synthetic_player_dialogue_history")
            or normalized.startswith("delete from synthetic_player_dialogue_history")
        ):
            if writer.submit(sql, params):
                return True
        conn = self.server.db._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(sql, params or ())
            return True
        except Exception:
            log.exception("FakePlayerManager SQL failed")
            return False
        finally:
            conn.close()
