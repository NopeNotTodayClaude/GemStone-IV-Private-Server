from __future__ import annotations

import time
from typing import Any


def evaluate_ready_rule(rule: dict | None, *, session, server, target=None, rank: int = 0) -> dict[str, Any]:
    """Evaluate a loader-defined action readiness rule against live state."""
    if not isinstance(rule, dict):
        return {"ready": False, "ready_until": None, "message": ""}

    message = str(rule.get("message") or "").strip()

    any_of = rule.get("any_of")
    if isinstance(any_of, list):
        matched = [
            evaluate_ready_rule(entry, session=session, server=server, target=target, rank=rank)
            for entry in any_of
            if isinstance(entry, dict)
        ]
        ready_rows = [row for row in matched if row.get("ready")]
        return {
            "ready": bool(ready_rows),
            "ready_until": _merge_any_until([row.get("ready_until") for row in ready_rows]),
            "message": message or next((row.get("message", "") for row in matched if row.get("message")), ""),
        }

    all_of = rule.get("all_of")
    if isinstance(all_of, list):
        matched = [
            evaluate_ready_rule(entry, session=session, server=server, target=target, rank=rank)
            for entry in all_of
            if isinstance(entry, dict)
        ]
        ready = bool(matched) and all(row.get("ready") for row in matched)
        return {
            "ready": ready,
            "ready_until": _merge_all_until([row.get("ready_until") for row in matched]) if ready else None,
            "message": message or next((row.get("message", "") for row in matched if row.get("message")), ""),
        }

    kind = str(rule.get("kind") or "").strip().lower()
    if kind == "target_required":
        live_target = _normalize_target(target)
        return {"ready": live_target is not None, "ready_until": None, "message": message}

    if kind == "reaction_trigger":
        triggers = _listify(rule.get("triggers"))
        trigger = str(rule.get("trigger") or "").strip().lower()
        if trigger:
            triggers.insert(0, trigger)
        now_mono = time.monotonic()
        now_wall = time.time()
        active_until = []
        reaction_triggers = getattr(session, "reaction_triggers", {}) or {}
        for name in triggers:
            expiry = float(reaction_triggers.get(name, 0) or 0)
            if expiry > now_mono:
                active_until.append(now_wall + max(0.0, expiry - now_mono))
        return {
            "ready": bool(active_until),
            "ready_until": max(active_until) if active_until else None,
            "message": message,
        }

    if kind == "player_hidden":
        return {
            "ready": bool(getattr(session, "hidden", False)),
            "ready_until": None,
            "message": message,
        }

    if kind == "player_status_any":
        matches = _status_matches(server, session, _listify(rule.get("statuses")))
        return {
            "ready": bool(matches),
            "ready_until": _merge_any_until([row["until"] for row in matches]),
            "message": message,
        }

    live_target = _normalize_target(target)
    if kind == "target_status_any":
        matches = _status_matches(server, live_target, _listify(rule.get("statuses")))
        return {
            "ready": bool(matches),
            "ready_until": _merge_any_until([row["until"] for row in matches]),
            "message": message,
        }

    if kind == "target_status_all":
        statuses = _listify(rule.get("statuses"))
        matches = _status_matches(server, live_target, statuses)
        ready = live_target is not None and len(matches) == len(statuses)
        return {
            "ready": ready,
            "ready_until": _merge_all_until([row["until"] for row in matches]) if ready else None,
            "message": message,
        }

    if kind == "target_flag_any":
        matches = _flag_matches(server, live_target, _listify(rule.get("flags")))
        return {
            "ready": bool(matches),
            "ready_until": _merge_any_until([row["until"] for row in matches]),
            "message": message,
        }

    if kind == "target_health_at_or_below":
        if live_target is None:
            return {"ready": False, "ready_until": None, "message": message}
        pct = float(rule.get("percent", 0) or 0)
        if pct <= 0:
            pct = float(rule.get("percent_per_rank", 0) or 0) * float(rank or 0)
        cap = int(rule.get("max_health_cap", 0) or 0)
        max_health = int(getattr(live_target, "health_max", 0) or 0)
        current_health = int(getattr(live_target, "health_current", 0) or 0)
        if max_health <= 0 or pct <= 0:
            return {"ready": False, "ready_until": None, "message": message}
        health_basis = min(max_health, cap) if cap > 0 else max_health
        threshold = health_basis * (pct / 100.0)
        return {
            "ready": current_health <= threshold,
            "ready_until": None,
            "message": message,
        }

    return {"ready": False, "ready_until": None, "message": message}


def _normalize_target(target):
    if target is None or getattr(target, "is_dead", False):
        return None
    if hasattr(target, "alive") and not getattr(target, "alive", True):
        return None
    return target


def _listify(value: Any) -> list[str]:
    if isinstance(value, (list, tuple, set)):
        return [str(entry).strip().lower() for entry in value if str(entry).strip()]
    text = str(value or "").strip().lower()
    return [text] if text else []


def _status_matches(server, entity, statuses: list[str]) -> list[dict[str, Any]]:
    if not entity:
        return []
    out = []
    for status_id in statuses:
        until = _entity_status_until(server, entity, status_id)
        if until is not False:
            out.append({"status": status_id, "until": until})
    return out


def _flag_matches(server, entity, flags: list[str]) -> list[dict[str, Any]]:
    if not entity:
        return []
    out = []
    for flag in flags:
        until = _entity_flag_until(server, entity, flag)
        if until is not False:
            out.append({"flag": flag, "until": until})
    return out


def _entity_flag_until(server, entity, flag: str):
    normalized = str(flag or "").strip().lower()
    if not normalized:
        return False

    status_until = _entity_status_until(server, entity, normalized)
    if status_until is not False:
        return status_until

    for attr_name in (normalized, f"is_{normalized}"):
        if hasattr(entity, attr_name):
            value = getattr(entity, attr_name)
            if callable(value):
                try:
                    value = value()
                except TypeError:
                    value = False
            if bool(value):
                return None

    for field_name in ("flags", "traits", "keywords", "movement_modes", "movement_tags", "tags", "abilities"):
        values = getattr(entity, field_name, None)
        if isinstance(values, (list, tuple, set)):
            lowered = {str(entry).strip().lower() for entry in values if str(entry).strip()}
            if normalized in lowered:
                return None

    return False


def _entity_status_until(server, entity, effect_id: str):
    normalized = str(effect_id or "").strip().lower()
    if not normalized or entity is None:
        return False

    status_mgr = getattr(server, "status", None)
    if status_mgr and hasattr(status_mgr, "has") and status_mgr.has(entity, normalized):
        effect = (getattr(entity, "status_effects", None) or {}).get(normalized)
        return _effect_until(effect)

    effects = getattr(entity, "status_effects", None) or {}
    effect = effects.get(normalized)
    if not effect:
        return False
    active = getattr(effect, "active", True)
    if not active:
        return False
    return _effect_until(effect)


def _effect_until(effect):
    if not effect:
        return None
    expires = float(getattr(effect, "expires", 0) or 0)
    if expires < 0:
        return None
    if expires > time.time():
        return expires
    return False


def _merge_any_until(values: list[Any]):
    if not values:
        return None
    if any(value is None for value in values):
        return None
    finite = [float(value) for value in values if value not in (None, False)]
    return max(finite) if finite else None


def _merge_all_until(values: list[Any]):
    if not values:
        return None
    finite = [float(value) for value in values if value not in (None, False)]
    if not finite:
        return None
    return min(finite)
