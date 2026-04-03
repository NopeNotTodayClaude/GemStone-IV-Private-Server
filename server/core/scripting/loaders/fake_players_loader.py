"""
fake_players_loader.py
----------------------
Loads scripts/data/fake_players.lua into normalized Python dictionaries.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def _to_int(value, default=0):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return int(default)


def _to_float(value, default=0.0):
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return float(default)


def _to_str(value, default=""):
    text = str(value or default).strip()
    return text if text else str(default or "")


def _to_list(values):
    if values is None:
        return []
    if isinstance(values, (list, tuple)):
        return list(values)
    return [values]


def _to_str_list(values):
    items = []
    for raw in _to_list(values):
        text = _to_str(raw, "")
        if text:
            items.append(text)
    return items


def _to_int_list(values):
    items = []
    for raw in _to_list(values):
        try:
            rid = int(raw)
        except (TypeError, ValueError):
            continue
        if rid > 0 and rid not in items:
            items.append(rid)
    return items


def _normalize_weight_rows(rows, id_key, label_key):
    out = []
    for row in _to_list(rows):
        if not isinstance(row, dict):
            continue
        item_id = _to_int(row.get(id_key), 0)
        label = _to_str(row.get(label_key), "")
        weight = max(1, _to_int(row.get("weight"), 1))
        if item_id <= 0 or not label:
            continue
        out.append({
            id_key: item_id,
            label_key: label,
            "weight": weight,
        })
    return out


def load_fake_players(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        log.warning("fake_players_loader: Lua engine unavailable")
        return {
            "defaults": {},
            "level_rules": {},
            "races": [],
            "professions": [],
            "mbti": {},
            "archetypes": {},
            "names": {"first": [], "last": []},
            "dialogue": {},
            "dialogue_builders": {},
            "argument_topics": {},
            "outfits": {},
            "gear": {},
            "intent_tokens": {},
            "regions": {},
        }

    try:
        data = lua_engine.load_data("data/fake_players") or {}
        if not isinstance(data, dict):
            raise RuntimeError("fake_players.lua did not return a dict")

        defaults_raw = data.get("defaults") or {}
        level_rules_raw = data.get("level_rules") or {}
        names_raw = data.get("names") or {}
        dialogue_raw = data.get("dialogue") or {}
        regions_raw = data.get("regions") or {}

        defaults = {
            "max_distance_from_player": max(1, _to_int(defaults_raw.get("max_distance_from_player"), 50)),
            "login_city_scope_radius": max(10, _to_int(defaults_raw.get("login_city_scope_radius"), 140)),
            "population_per_player": max(1, _to_int(defaults_raw.get("population_per_player"), 7)),
            "max_total_population": max(1, _to_int(defaults_raw.get("max_total_population"), 36)),
            "min_population_with_players": max(0, _to_int(defaults_raw.get("min_population_with_players"), 6)),
            "population_target_refresh_seconds": max(15, _to_int(defaults_raw.get("population_target_refresh_seconds"), 180)),
            "spawn_batch_size": max(1, _to_int(defaults_raw.get("spawn_batch_size"), 5)),
            "spawn_batch_interval_seconds": max(1, _to_int(defaults_raw.get("spawn_batch_interval_seconds"), 2)),
            "city_population_floor": max(0, _to_int(defaults_raw.get("city_population_floor"), 40)),
            "city_population_ceiling": max(0, _to_int(defaults_raw.get("city_population_ceiling"), 60)),
            "town_population_floor": max(0, _to_int(defaults_raw.get("town_population_floor"), 18)),
            "town_population_ceiling": max(0, _to_int(defaults_raw.get("town_population_ceiling"), 32)),
            "wilds_population_floor": max(0, _to_int(defaults_raw.get("wilds_population_floor"), 4)),
            "wilds_population_ceiling": max(0, _to_int(defaults_raw.get("wilds_population_ceiling"), 12)),
            "social_tick_seconds": max(1, _to_int(defaults_raw.get("social_tick_seconds"), 5)),
            "behavior_tick_seconds": max(1, _to_int(defaults_raw.get("behavior_tick_seconds"), 10)),
            "save_tick_seconds": max(5, _to_int(defaults_raw.get("save_tick_seconds"), 60)),
            "save_interval_sec": max(5, _to_int(defaults_raw.get("save_interval_sec"), _to_int(defaults_raw.get("save_tick_seconds"), 60))),
            "justice_id_offset": max(1000000, _to_int(defaults_raw.get("justice_id_offset"), 1000000000)),
            "idle_xp_gain": max(0, _to_int(defaults_raw.get("idle_xp_gain"), 35)),
            "sleep_xp_gain": max(0, _to_int(defaults_raw.get("sleep_xp_gain"), 120)),
            "hunt_xp_gain": max(0, _to_int(defaults_raw.get("hunt_xp_gain"), 250)),
            "idle_field_xp_gain": max(0, _to_int(defaults_raw.get("idle_field_xp_gain"), _to_int(defaults_raw.get("idle_xp_gain"), 35))),
            "sleep_field_xp_gain": max(0, _to_int(defaults_raw.get("sleep_field_xp_gain"), _to_int(defaults_raw.get("sleep_xp_gain"), 120))),
            "hunt_field_xp_gain": max(0, _to_int(defaults_raw.get("hunt_field_xp_gain"), _to_int(defaults_raw.get("hunt_xp_gain"), 250))),
            "crime_cooldown_seconds": max(60, _to_int(defaults_raw.get("crime_cooldown_seconds"), 900)),
            "dialogue_repeat_actor_seconds": max(60, _to_int(defaults_raw.get("dialogue_repeat_actor_seconds"), 720)),
            "dialogue_repeat_global_seconds": max(60, _to_int(defaults_raw.get("dialogue_repeat_global_seconds"), 300)),
            "dialogue_pair_cooldown_seconds": max(8, _to_int(defaults_raw.get("dialogue_pair_cooldown_seconds"), 90)),
            "argument_thread_seconds": max(30, _to_int(defaults_raw.get("argument_thread_seconds"), 900)),
            "argument_reply_min_seconds": max(3, _to_int(defaults_raw.get("argument_reply_min_seconds"), 15)),
            "argument_reply_max_seconds": max(3, _to_int(defaults_raw.get("argument_reply_max_seconds"), 45)),
            "conversation_thread_seconds": max(30, _to_int(defaults_raw.get("conversation_thread_seconds"), 420)),
            "conversation_reply_min_seconds": max(3, _to_int(defaults_raw.get("conversation_reply_min_seconds"), 12)),
            "conversation_reply_max_seconds": max(3, _to_int(defaults_raw.get("conversation_reply_max_seconds"), 30)),
            "intent_prompt_seconds": max(6, _to_int(defaults_raw.get("intent_prompt_seconds"), 28)),
            "intent_announce_cooldown_seconds": max(30, _to_int(defaults_raw.get("intent_announce_cooldown_seconds"), 240)),
            "spam_window_seconds": max(6, _to_int(defaults_raw.get("spam_window_seconds"), 18)),
            "spam_line_threshold": max(2, _to_int(defaults_raw.get("spam_line_threshold"), 4)),
            "spam_repeat_threshold": max(2, _to_int(defaults_raw.get("spam_repeat_threshold"), 2)),
            "spam_yell_threshold": max(2, _to_int(defaults_raw.get("spam_yell_threshold"), 3)),
            "safe_room_task_suppression": max(0.0, min(0.98, _to_float(defaults_raw.get("safe_room_task_suppression"), 0.34))),
            "safe_room_linger_base": max(0.0, min(0.98, _to_float(defaults_raw.get("safe_room_linger_base"), 0.18))),
            "safe_room_social_min_delay": max(1, _to_int(defaults_raw.get("safe_room_social_min_delay"), 2)),
            "safe_room_social_max_delay": max(1, _to_int(defaults_raw.get("safe_room_social_max_delay"), 5)),
            "service_task_chance_safe": max(0.0, min(1.0, _to_float(defaults_raw.get("service_task_chance_safe"), 0.20))),
            "town_afk_emote_chance": max(0.0, min(1.0, _to_float(defaults_raw.get("town_afk_emote_chance"), 0.24))),
            "safe_room_crowd_spill_threshold": max(2, _to_int(defaults_raw.get("safe_room_crowd_spill_threshold"), 4)),
            "safe_room_crowd_spill_chance": max(0.0, min(1.0, _to_float(defaults_raw.get("safe_room_crowd_spill_chance"), 0.78))),
            "spawn_room_soft_cap": max(1, _to_int(defaults_raw.get("spawn_room_soft_cap"), 3)),
            "travel_spawn_weight": max(0.0, min(1.0, _to_float(defaults_raw.get("travel_spawn_weight"), 0.08))),
            "travel_roam_weight": max(0.0, min(1.0, _to_float(defaults_raw.get("travel_roam_weight"), 0.18))),
            "planner_workers": max(0, _to_int(defaults_raw.get("planner_workers"), 2)),
            "planner_queue_multiplier": max(1, _to_int(defaults_raw.get("planner_queue_multiplier"), 4)),
            "planner_submit_per_tick": max(1, _to_int(defaults_raw.get("planner_submit_per_tick"), 18)),
            "actor_updates_per_tick": max(1, _to_int(defaults_raw.get("actor_updates_per_tick"), 18)),
            "expensive_action_min_seconds": max(1, _to_int(defaults_raw.get("expensive_action_min_seconds"), 12)),
            "expensive_action_max_seconds": max(1, _to_int(defaults_raw.get("expensive_action_max_seconds"), 26)),
            "path_cache_seconds": max(1, _to_int(defaults_raw.get("path_cache_seconds"), 45)),
            "distance_cache_seconds": max(1, _to_int(defaults_raw.get("distance_cache_seconds"), 90)),
            "perf_log_interval_seconds": max(5, _to_int(defaults_raw.get("perf_log_interval_seconds"), 60)),
            "dialogue_builder_disabled_keys": _to_str_list(defaults_raw.get("dialogue_builder_disabled_keys") or []),
            "interaction_memory_cap": max(1, _to_int(defaults_raw.get("interaction_memory_cap"), 24)),
            "region_weight_city": max(0.01, _to_float(defaults_raw.get("region_weight_city"), 1.0)),
            "region_weight_town": max(0.01, _to_float(defaults_raw.get("region_weight_town"), 0.45)),
            "region_weight_wilds": max(0.0, _to_float(defaults_raw.get("region_weight_wilds"), 0.12)),
        }

        level_rules = {
            "min_level": max(1, _to_int(level_rules_raw.get("min_level"), 1)),
            "max_level": max(1, _to_int(level_rules_raw.get("max_level"), 100)),
            "below_average_floor": max(0, _to_int(level_rules_raw.get("below_average_floor"), 6)),
            "below_average_cap": max(0, _to_int(level_rules_raw.get("below_average_cap"), 2)),
            "above_average_cap": max(0, _to_int(level_rules_raw.get("above_average_cap"), 4)),
            "wilderness_bias": max(0, _to_int(level_rules_raw.get("wilderness_bias"), 2)),
        }

        mbti = {}
        for key, row in (data.get("mbti") or {}).items():
            if not isinstance(row, dict):
                continue
            mbti_key = _to_str(key, "").upper()
            if not mbti_key:
                continue
            mbti[mbti_key] = {
                "social": max(0.0, min(1.0, _to_float(row.get("social"), 0.3))),
                "rude": max(0.0, min(1.0, _to_float(row.get("rude"), 0.05))),
                "shy": max(0.0, min(1.0, _to_float(row.get("shy"), 0.10))),
                "hunt": max(0.0, min(1.0, _to_float(row.get("hunt"), 0.15))),
                "craft": max(0.0, min(1.0, _to_float(row.get("craft"), 0.10))),
                "roam": max(0.0, min(1.0, _to_float(row.get("roam"), 0.20))),
                "player_reply": max(0.0, min(1.0, _to_float(row.get("player_reply"), 0.45))),
                "crime": max(0.0, min(1.0, _to_float(row.get("crime"), 0.02))),
            }

        archetypes = {}
        for key, row in (data.get("archetypes") or {}).items():
            if not isinstance(row, dict):
                continue
            archetype_key = _to_str(key, "").strip().lower()
            if not archetype_key:
                continue
            archetypes[archetype_key] = {
                "weight": max(1, _to_int(row.get("weight"), 1)),
                "idle_bias": max(0.0, _to_float(row.get("idle_bias"), 0.0)),
                "inn_bias": max(0.0, _to_float(row.get("inn_bias"), 0.0)),
                "hunt_bias": max(0.0, _to_float(row.get("hunt_bias"), 0.0)),
                "pawn_bias": max(0.0, _to_float(row.get("pawn_bias"), 0.0)),
                "locksmith_bias": max(0.0, _to_float(row.get("locksmith_bias"), 0.0)),
                "craft_bias": max(0.0, _to_float(row.get("craft_bias"), 0.0)),
                "justice_bias": max(0.0, _to_float(row.get("justice_bias"), 0.0)),
            }

        dialogue = {
            key: _to_str_list(values)
            for key, values in dialogue_raw.items()
            if _to_str_list(values)
        }

        regions = {}
        for region_id, row in regions_raw.items():
            if not isinstance(row, dict):
                continue
            key = _to_str(region_id, "").strip().lower()
            if not key:
                continue
            anchors = _to_int_list(row.get("anchor_room_ids"))
            if not anchors:
                continue
            regions[key] = {
                "id": key,
                "display_name": _to_str(row.get("display_name"), key),
                "kind": _to_str(row.get("kind"), "town").strip().lower(),
                "jurisdiction_id": _to_str(row.get("jurisdiction_id"), "").strip().lower(),
                "anchor_room_ids": anchors,
                "hotspot_room_ids": _to_int_list(row.get("hotspot_room_ids")),
                "rest_room_ids": _to_int_list(row.get("rest_room_ids")),
                "crafting_room_ids": _to_int_list(row.get("crafting_room_ids")),
                "travel_room_ids": _to_int_list(row.get("travel_room_ids")),
            }

        result = {
            "defaults": defaults,
            "level_rules": level_rules,
            "races": _normalize_weight_rows(data.get("races"), "race_id", "name"),
            "professions": _normalize_weight_rows(data.get("professions"), "profession_id", "name"),
            "mbti": mbti,
            "archetypes": archetypes,
            "names": {
                "first": _to_str_list(names_raw.get("first")),
                "last": _to_str_list(names_raw.get("last")),
            },
            "dialogue": dialogue,
            "dialogue_builders": dict(data.get("dialogue_builders") or {}),
            "argument_topics": dict(data.get("argument_topics") or {}),
            "outfits": dict(data.get("outfits") or {}),
            "gear": dict(data.get("gear") or {}),
            "intent_tokens": dict(data.get("intent_tokens") or {}),
            "regions": regions,
        }
        log.info(
            "fake_players_loader: loaded %d regions, %d MBTI profiles, %d archetypes",
            len(result["regions"]),
            len(result["mbti"]),
            len(result["archetypes"]),
        )
        return result
    except Exception as e:
        log.error("fake_players_loader: failed to load fake_players.lua (%s)", e, exc_info=True)
        return {
            "defaults": {},
            "level_rules": {},
            "races": [],
            "professions": [],
            "mbti": {},
            "archetypes": {},
            "names": {"first": [], "last": []},
            "dialogue": {},
            "regions": {},
        }
