"""
creature_spawns_loader.py
-------------------------
Loads scripts/data/creature_spawns.lua for CreatureManager runtime settings.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def load_creature_spawns(engine) -> dict:
    if not engine or not engine.available:
        return {"defaults": {
            "active_player_bubble_rooms": 60,
            "planner_workers": 0,
            "planner_queue_multiplier": 2,
            "planner_submit_interval_ticks": 30,
            "wander_submit_interval_ticks": 150,
            "perf_log_interval_seconds": 60,
        }}
    try:
        data = engine.load_data("data/creature_spawns") or {}
        defaults = dict(data.get("defaults") or {}) if isinstance(data, dict) else {}
        bubble = int(defaults.get("active_player_bubble_rooms") or 60)
        out = {"defaults": {
            "active_player_bubble_rooms": max(1, bubble),
            "planner_workers": max(0, int(defaults.get("planner_workers") or 0)),
            "planner_queue_multiplier": max(1, int(defaults.get("planner_queue_multiplier") or 2)),
            "planner_submit_interval_ticks": max(5, int(defaults.get("planner_submit_interval_ticks") or 30)),
            "wander_submit_interval_ticks": max(10, int(defaults.get("wander_submit_interval_ticks") or 150)),
            "perf_log_interval_seconds": max(15, int(defaults.get("perf_log_interval_seconds") or 60)),
        }}
        log.info("creature_spawns_loader: loaded creature spawn settings from Lua")
        return out
    except Exception as e:
        log.error("creature_spawns_loader: failed to load creature_spawns.lua: %s", e, exc_info=True)
        return {"defaults": {
            "active_player_bubble_rooms": 60,
            "planner_workers": 0,
            "planner_queue_multiplier": 2,
            "planner_submit_interval_ticks": 30,
            "wander_submit_interval_ticks": 150,
            "perf_log_interval_seconds": 60,
        }}
