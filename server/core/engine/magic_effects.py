"""
Helpers for reading active magic/item effect rows from character_active_buffs.

This keeps the rest of the codebase from open-coding the same DB lookups for
visibility, encumbrance, roundtime, and utility bonuses.
"""

from __future__ import annotations


def _character_id(entity) -> int:
    if not entity:
        return 0
    return int(getattr(entity, "character_id", 0) or 0)


def get_active_buff_totals(server, entity) -> dict:
    db = getattr(server, "db", None)
    character_id = _character_id(entity)
    if not db or not character_id:
        return {}
    try:
        return db.get_active_buff_effect_totals(character_id) or {}
    except Exception:
        return {}


def effect_value(server, entity, key: str, default=0):
    buffs = get_active_buff_totals(server, entity)
    return buffs.get(key, default)


def has_effect(server, entity, key: str) -> bool:
    return bool(effect_value(server, entity, key, False))


def can_see_hidden(server, viewer) -> bool:
    return has_effect(server, viewer, "see_hidden")


def can_see_invisible(server, viewer) -> bool:
    return has_effect(server, viewer, "see_invisible")


def is_invisible(server, entity) -> bool:
    return has_effect(server, entity, "invisible")


def is_visible_to(server, viewer, target) -> bool:
    if not target:
        return False
    if getattr(target, "hidden", False) and not can_see_hidden(server, viewer):
        return False
    if is_invisible(server, target) and not can_see_invisible(server, viewer):
        return False
    return True


def apply_roundtime_effects(base_rt: int, server, entity, *, is_bolt: bool = False) -> int:
    rt = int(base_rt or 0)
    buffs = get_active_buff_totals(server, entity)
    rt -= int(buffs.get("rt_reduction", 0) or 0)
    if is_bolt:
        rt -= int(buffs.get("bolt_rt_reduction", 0) or 0)
    rt += int(buffs.get("rt_penalty", 0) or 0)
    rt = int(rt * max(0.0, 1.0 - (float(buffs.get("rt_reduction_pct", 0) or 0) / 100.0)))
    return rt

