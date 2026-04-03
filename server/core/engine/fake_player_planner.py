"""
Worker-safe synthetic-player planning helpers.

This module contains only pure planning logic so it can run in a
ProcessPoolExecutor without touching live server state.
"""

from __future__ import annotations

import random


def _clamp(value, low, high):
    return max(low, min(high, value))


def _weighted_choice(rows, rng: random.Random):
    rows = [(row, max(0.0, float(weight))) for row, weight in rows if max(0.0, float(weight)) > 0.0]
    if not rows:
        return None
    total = sum(weight for _, weight in rows)
    roll = rng.uniform(0.0, total or 1.0)
    upto = 0.0
    for row, weight in rows:
        upto += weight
        if roll <= upto:
            return row
    return rows[-1][0]


def plan_actor_action(payload: dict) -> dict:
    seed = int(payload.get("seed") or 0)
    rng = random.Random(seed)

    if not payload.get("has_room"):
        return {"action": "spawn", "delay_min": 2.0, "delay_max": 5.0}

    if payload.get("blocked_status"):
        return {"action": "wait", "delay_min": 6.0, "delay_max": 12.0}

    room_safe = bool(payload.get("room_safe"))
    occupants = int(payload.get("occupants") or 0)
    synthetic_count = int(payload.get("synthetic_count") or 0)
    real_player_present = bool(payload.get("real_player_present"))
    social_bias = float(payload.get("social_bias") or 0.25)
    rude_bias = float(payload.get("rude_bias") or 0.12)
    craft_bias = float(payload.get("craft_bias") or 0.15)
    roam_bias = float(payload.get("roam_bias") or 0.20)
    hunt_bias = float(payload.get("hunt_bias") or 0.18)
    crime_bias = float(payload.get("crime_bias") or 0.03)
    inn_bias = float(payload.get("inn_bias") or 0.10)
    idle_bias = float(payload.get("idle_bias") or 0.55)
    pawn_bias = float(payload.get("pawn_bias") or 0.10)
    locksmith_bias = float(payload.get("locksmith_bias") or 0.10)
    safe_room_suppression = float(payload.get("safe_room_suppression") or 0.34)

    if room_safe:
        spill_threshold = max(2, int(payload.get("spill_threshold") or 4))
        spill_chance = float(payload.get("spill_chance") or 0.78)
        if synthetic_count >= spill_threshold and payload.get("roam_candidates") and rng.random() < spill_chance:
            target = _weighted_choice(
                [({"room_id": row["room_id"]}, float(row.get("weight") or 1.0)) for row in (payload.get("roam_candidates") or [])],
                rng,
            )
            if target:
                return {"action": "roam", "target_room_id": int(target["room_id"]), "delay_min": 4.0, "delay_max": 9.0}

        crowded_bonus = min(0.24, max(0.0, occupants) * 0.06)
        real_player_bonus = 0.22 if real_player_present else 0.0
        social_chance = min(0.92, 0.18 + social_bias * 0.90 + rude_bias * 0.18 + crowded_bonus + real_player_bonus)
        if rng.random() < social_chance:
            return {
                "action": "social",
                "delay_min": float(payload.get("safe_room_social_min_delay") or 2),
                "delay_max": float(payload.get("safe_room_social_max_delay") or 6),
            }

        linger_roll = float(payload.get("safe_room_linger_base") or 0.18) + (idle_bias * 0.22) + crowded_bonus + real_player_bonus
        if rng.random() < min(0.96, linger_roll) and rng.random() < float(payload.get("town_afk_emote_chance") or 0.24):
            return {"action": "afk_emote", "delay_min": 2.0, "delay_max": 5.0}

        if rng.random() < safe_room_suppression:
            return {"action": "wait", "delay_min": 2.0, "delay_max": 5.5}

    if payload.get("can_service"):
        safe_task_gate = 1.0
        if room_safe:
            safe_task_gate = max(
                0.02,
                float(payload.get("service_task_chance_safe") or 0.20)
                * (0.55 + locksmith_bias + pawn_bias)
                * (1.0 - safe_room_suppression),
            )
        if rng.random() < safe_task_gate:
            service_rows = []
            if payload.get("can_locksmith_customer"):
                service_rows.append(("locksmith_customer", 1.0 + locksmith_bias))
            if payload.get("can_locksmith_rogue"):
                service_rows.append(("locksmith_rogue", 0.85 + locksmith_bias))
            if payload.get("can_pawn"):
                service_rows.append(("pawn", 0.85 + pawn_bias))
            pick = _weighted_choice(service_rows, rng)
            if pick:
                return {"action": pick, "delay_min": 14.0, "delay_max": 24.0}

    if payload.get("can_inn") and (
        payload.get("has_inn_stay")
        or payload.get("at_inn_front_desk")
        or rng.random() < max(0.04, min(0.32, inn_bias))
    ):
        return {"action": "inn", "delay_min": 12.0, "delay_max": 26.0}

    if payload.get("can_lawbreak") and rng.random() < crime_bias:
        return {"action": "lawbreak", "delay_min": 20.0, "delay_max": 45.0}

    if payload.get("can_hunt"):
        hunt_rows = []
        for row in payload.get("hunt_candidates") or []:
            gap = int(row.get("gap") or 99)
            weight = max(0.05, 1.8 - (gap * 0.18)) * max(0.05, hunt_bias)
            hunt_rows.append((row, weight))
        if hunt_rows and rng.random() < max(0.05, hunt_bias):
            pick = _weighted_choice(hunt_rows, rng)
            if pick:
                if pick.get("room_id") == payload.get("current_room_id"):
                    return {"action": "hunt_here", "delay_min": 6.0, "delay_max": 14.0}
                return {"action": "hunt_move", "target_room_id": int(pick["room_id"]), "delay_min": 6.0, "delay_max": 14.0}

    if payload.get("can_forage") and rng.random() < max(0.08, craft_bias * 0.55):
        forage_rooms = list(payload.get("forage_candidates") or [])
        if forage_rooms:
            target_room_id = int(rng.choice(forage_rooms))
            if target_room_id == int(payload.get("current_room_id") or 0):
                return {"action": "forage_here", "delay_min": 8.0, "delay_max": 18.0}
            return {"action": "forage_move", "target_room_id": target_room_id, "delay_min": 8.0, "delay_max": 18.0}

    misc_rows = [
        ("social", max(0.05, social_bias)),
        ("craft", max(0.05, craft_bias)),
        ("roam", max(0.05, roam_bias)),
        ("wait", max(0.10, 0.35 - social_bias)),
    ]
    pick = _weighted_choice(misc_rows, rng) or "wait"
    if pick == "roam" and payload.get("roam_candidates"):
        target = _weighted_choice(
            [({"room_id": row["room_id"]}, float(row.get("weight") or 1.0)) for row in (payload.get("roam_candidates") or [])],
            rng,
        )
        if target:
            return {"action": "roam", "target_room_id": int(target["room_id"]), "delay_min": 8.0, "delay_max": 18.0}
        pick = "wait"

    if pick == "wait":
        return {"action": "wait", "delay_min": 6.0, "delay_max": 16.0}
    if pick == "craft":
        return {"action": "craft", "delay_min": 8.0, "delay_max": 18.0}
    if pick == "social":
        return {"action": "social", "delay_min": 8.0, "delay_max": 18.0}
    return {"action": "wait", "delay_min": 6.0, "delay_max": 16.0}
