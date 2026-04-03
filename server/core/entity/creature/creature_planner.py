"""
creature_planner.py
-------------------
Worker-safe creature AI planning.
"""

from __future__ import annotations

import random


def plan_creature_actions(payload: dict) -> list[dict]:
    creatures = list(payload.get("creatures") or [])
    players = list(payload.get("players") or [])
    player_by_session = {int(row.get("session_id") or 0): row for row in players if int(row.get("session_id") or 0) > 0}
    players_by_room: dict[int, list[dict]] = {}
    for row in players:
        room_id = int(row.get("room_id") or 0)
        if room_id <= 0:
            continue
        players_by_room.setdefault(room_id, []).append(row)

    now = float(payload.get("now") or 0.0)
    allow_wander = bool(payload.get("allow_wander", False))
    hunting_rooms = {int(row) for row in (payload.get("hunting_rooms") or []) if int(row or 0) > 0}
    seed = int(payload.get("seed") or 0)
    rng = random.Random(seed)
    actions: list[dict] = []

    for creature in creatures:
        creature_id = int(creature.get("id") or 0)
        room_id = int(creature.get("room_id") or 0)
        if creature_id <= 0 or room_id <= 0 or not creature.get("alive", False):
            continue
        if float(creature.get("roundtime_end") or 0.0) > now:
            continue
        if float(creature.get("stunned_until") or 0.0) > now:
            continue

        if creature.get("in_combat", False):
            target_id = int(creature.get("target_session_id") or 0)
            target = player_by_session.get(target_id)
            if not target:
                actions.append({"kind": "clear_target", "creature_id": creature_id})
                continue
            if not (
                target.get("state") == "playing"
                and not target.get("hidden", False)
                and not target.get("invisible", False)
                and not target.get("is_dead", False)
                and int(target.get("room_id") or 0) == room_id
            ):
                actions.append({"kind": "clear_target", "creature_id": creature_id})
                continue
            actions.append({"kind": "attack", "creature_id": creature_id, "target_session_id": target_id})
            continue

        if creature.get("aggressive", False):
            visible = [
                row for row in (players_by_room.get(room_id) or [])
                if row.get("state") == "playing"
                and not row.get("hidden", False)
                and not row.get("invisible", False)
                and not row.get("is_dead", False)
            ]
            if visible:
                target = rng.choice(visible)
                actions.append({
                    "kind": "engage",
                    "creature_id": creature_id,
                    "target_session_id": int(target.get("session_id") or 0),
                })
                continue

        if not allow_wander or not creature.get("can_wander", False):
            continue
        if rng.random() > float(creature.get("wander_chance") or 0.0):
            continue
        exits = dict(creature.get("exits") or {})
        candidates = []
        wander_rooms = {int(row) for row in (creature.get("wander_rooms") or []) if int(row or 0) > 0}
        for direction, target_room_id in exits.items():
            target_room_id = int(target_room_id or 0)
            if target_room_id <= 0 or target_room_id not in hunting_rooms:
                continue
            if wander_rooms and target_room_id not in wander_rooms:
                continue
            candidates.append({"direction": str(direction or "out"), "target_room_id": target_room_id})
        if not candidates:
            continue
        chosen = rng.choice(candidates)
        actions.append({
            "kind": "wander",
            "creature_id": creature_id,
            "target_room_id": int(chosen["target_room_id"]),
            "direction": str(chosen["direction"]),
        })
    return actions
