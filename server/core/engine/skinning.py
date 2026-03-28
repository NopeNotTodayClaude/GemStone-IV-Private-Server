"""
skinning.py
-----------
GS4-style skinning resolution using Lua-backed configuration and creature-
specific skin definitions.
"""

from __future__ import annotations

import random
from typing import Optional


SKILL_SURVIVAL = 23
SKILL_FIRST_AID = 30


def _skill_ranks(session, skill_id: int) -> int:
    skills = getattr(session, "skills", {}) or {}
    row = skills.get(skill_id, {})
    if isinstance(row, dict):
        return int(row.get("ranks", 0) or 0)
    return 0


def _stat_bonus(session, attr_name: str) -> int:
    return (int(getattr(session, attr_name, 50) or 50) - 50) // 2


def _open_d100() -> int:
    roll = random.randint(1, 100)
    if roll >= 96:
        roll += random.randint(1, 100)
    elif roll <= 5:
        roll -= random.randint(1, 100)
    return roll


def _get_config(server) -> dict:
    lua = getattr(server, "lua", None)
    if lua:
        try:
            cfg = lua.get_skinning()
            if isinstance(cfg, dict):
                return cfg
        except Exception:
            pass
    return {
        "settings": {},
        "quality_tiers": [],
        "tool_bonuses": {},
        "noun_values": {},
        "noun_difficulty": {},
        "item_overrides": {},
    }


def _tool_bonus_for_item(item, tool_bonuses: dict) -> Optional[int]:
    if not item:
        return None
    names = [
        str(item.get("short_name") or "").lower(),
        str(item.get("name") or "").lower(),
        str(item.get("noun") or "").lower(),
    ]
    best_bonus = None
    for key, value in (tool_bonuses or {}).items():
        key = str(key or "").lower().strip()
        if not key:
            continue
        if any(key in field for field in names):
            bonus = int(value)
            if best_bonus is None or bonus > best_bonus:
                best_bonus = bonus
    return best_bonus


def get_skinning_tool_bonus(item, server) -> Optional[int]:
    cfg = _get_config(server)
    return _tool_bonus_for_item(item, cfg.get("tool_bonuses", {}) or {})


def is_skinning_tool(item, server) -> bool:
    return get_skinning_tool_bonus(item, server) is not None


def find_best_skinning_tool(candidates, server):
    cfg = _get_config(server)
    best_item = None
    best_bonus = None
    for item in candidates or []:
        bonus = _tool_bonus_for_item(item, cfg.get("tool_bonuses", {}) or {})
        if bonus is None:
            continue
        if best_bonus is None or bonus > best_bonus:
            best_item = item
            best_bonus = bonus
    if best_item is None:
        return None, None
    return best_item, int(best_bonus or 0)


def get_skinning_sheath_nouns(server) -> set[str]:
    cfg = _get_config(server)
    raw = cfg.get("sheath_nouns") or {}
    if isinstance(raw, dict):
        return {
            str(noun).lower().strip()
            for noun, allowed in raw.items()
            if allowed
        }
    if isinstance(raw, (list, tuple, set)):
        return {str(noun).lower().strip() for noun in raw if noun}
    return set()


def _strip_article(name: str) -> tuple[str, str]:
    text = str(name or "").strip()
    lowered = text.lower()
    for article in ("an ", "a ", "the "):
        if lowered.startswith(article):
            bare = text[len(article):].strip()
            return article.strip(), bare
    return "a", text


def _find_skinning_tool(session, cfg: dict):
    candidates = []
    for hand_name in ("right_hand", "left_hand"):
        item = getattr(session, hand_name, None)
        if item:
            candidates.append(item)
    best_item = None
    best_bonus = None
    for item in candidates:
        bonus = _tool_bonus_for_item(item, cfg.get("tool_bonuses", {}) or {})
        if bonus is None:
            continue
        if best_bonus is None or bonus > best_bonus:
            best_item = item
            best_bonus = bonus
    if best_item is None:
        return None, None
    return best_item, int(best_bonus or 0)


def _resolve_skin_spec(creature, server) -> dict:
    cfg = _get_config(server)
    name = str(getattr(creature, "skin", "") or "").strip()
    article, bare = _strip_article(name)
    noun = bare.split()[-1].lower() if bare else "skin"

    overrides = cfg.get("item_overrides", {}) or {}
    override = overrides.get(name.lower()) or {}

    db = getattr(server, "db", None)
    template = db.get_item_template_by_short_name(name) if db else None

    base_value = 0
    if template:
        base_value = int(template.get("value") or 0)
        noun = str(template.get("noun") or noun).strip().lower() or noun
        article = str(template.get("article") or article).strip() or article
        bare = str(template.get("short_name") or bare).strip() or bare
    elif override.get("value"):
        base_value = int(override.get("value") or 0)
        noun = override.get("noun") or noun
    else:
        noun_values = cfg.get("noun_values", {}) or {}
        base_value = int(noun_values.get(noun, 25) or 25) + int(getattr(creature, "level", 1) or 1) * 4

    noun_difficulty = cfg.get("noun_difficulty", {}) or {}
    difficulty = int(getattr(creature, "level", 1) or 1) * int((cfg.get("settings", {}) or {}).get("difficulty_per_level", 3) or 3)
    difficulty += int(noun_difficulty.get(noun, 5) or 5)
    if override.get("difficulty"):
        difficulty = int(override.get("difficulty") or difficulty)

    return {
        "name": name,
        "article": article,
        "short_name": bare or name,
        "noun": noun,
        "base_value": max(1, int(base_value or 1)),
        "difficulty": max(1, int(difficulty or 1)),
    }


def _pick_quality(cfg: dict, margin: int) -> Optional[dict]:
    for row in cfg.get("quality_tiers", []) or []:
        if margin >= int(row.get("min_margin", 0) or 0):
            return row
    return None


def corpse_has_search_loot(creature) -> bool:
    treasure = getattr(creature, "treasure", {}) or {}
    return any(bool(treasure.get(key)) for key in ("coins", "gems", "magic", "boxes"))


def can_remove_corpse(creature) -> bool:
    searched = bool(getattr(creature, "searched", False))
    has_loot = corpse_has_search_loot(creature)
    has_skin = bool(getattr(creature, "skin", None))
    skinned = bool(getattr(creature, "skinned", False))
    return (searched or not has_loot) and (not has_skin or skinned)


def resolve_skinning(session, creature, server) -> dict:
    cfg = _get_config(server)
    settings = cfg.get("settings", {}) or {}
    spec = _resolve_skin_spec(creature, server)

    survival = _skill_ranks(session, SKILL_SURVIVAL) * int(settings.get("skill_rank_weight", 1) or 1)
    first_aid = _skill_ranks(session, SKILL_FIRST_AID) * int(settings.get("first_aid_weight", 1) or 1)
    dex_bonus = _stat_bonus(session, "stat_dexterity")
    agi_bonus = _stat_bonus(session, "stat_agility")
    stat_bonus = int(dex_bonus * float(settings.get("dexterity_weight", 0.5) or 0.5))
    stat_bonus += int(agi_bonus * float(settings.get("agility_weight", 0.5) or 0.5))

    tool, tool_bonus = _find_skinning_tool(session, cfg)
    if tool_bonus is None:
        tool_bonus = -int(settings.get("untooled_penalty", 35) or 35)

    roll = _open_d100()
    score = roll + survival + first_aid + stat_bonus + tool_bonus
    margin = score - int(spec["difficulty"])
    destroy_threshold = int(settings.get("destroy_threshold", -30) or -30)

    if margin < destroy_threshold:
        return {
            "success": False,
            "destroyed": True,
            "tool": tool,
            "roll": roll,
            "margin": margin,
            "spec": spec,
        }

    quality = _pick_quality(cfg, margin)
    if not quality:
        return {
            "success": False,
            "destroyed": True,
            "tool": tool,
            "roll": roll,
            "margin": margin,
            "spec": spec,
        }

    quality_key = str(quality.get("key") or "good")
    quality_label = str(quality.get("label") or quality_key)
    value = max(1, int(round(float(spec["base_value"]) * float(quality.get("value_multiplier") or 1.0))))

    item = {
        "name": spec["name"],
        "short_name": spec["short_name"],
        "noun": spec["noun"],
        "article": spec["article"],
        "item_type": "skin",
        "value": value,
        "skin_quality": quality_key,
        "quality_label": quality_label,
        "base_skin_name": spec["name"],
        "base_value": spec["base_value"],
        "description": f"{spec['name'].capitalize()} ({quality_label} quality).",
    }

    return {
        "success": True,
        "destroyed": False,
        "tool": tool,
        "roll": roll,
        "margin": margin,
        "quality": quality,
        "item": item,
        "spec": spec,
    }
