"""
combat_maneuvers_loader.py
--------------------------
Loads scripts/combat_maneuvers/definitions.lua and keeps the SQL maneuver
registry synchronized so Lua remains the source of truth.
"""

from __future__ import annotations

import logging
import re

log = logging.getLogger(__name__)


def load_combat_maneuvers(engine) -> dict | None:
    """Load scripts/combat_maneuvers/definitions.lua and return a Python dict."""
    if not engine or not engine.available:
        return None
    try:
        data = engine.require("combat_maneuvers/definitions")
        data = engine.lua_to_python(data) if data else None
        if isinstance(data, dict) and data:
            log.info("combat_maneuvers_loader: loaded %d maneuver defs", len(data))
            return data
        log.warning("combat_maneuvers_loader: empty or invalid definitions")
        return None
    except Exception as exc:
        log.error("combat_maneuvers_loader: failed to load definitions.lua: %s", exc, exc_info=True)
        return None


def _normalize_type(raw: str) -> str:
    key = str(raw or "").strip().lower().replace(" ", "_").replace("-", "_")
    mapping = {
        "area_of_effect": "aoe",
        "martial_stance": "martial_stance",
        "active_buff": "buff",
    }
    return mapping.get(key, key or "passive")


def _normalize_category(raw: str) -> str:
    key = str(raw or "").strip().lower().replace(" ", "_").replace("-", "_")
    if key in {"rogue_guild", "warrior_guild"}:
        return key
    return key or "general"


def _normalize_professions(raw) -> str:
    if isinstance(raw, str):
        text = raw.strip().lower()
        if not text or text == "all":
            return "warrior,rogue,wizard,cleric,empath,sorcerer,ranger,bard,paladin,monk"
        return text
    vals = []
    for entry in raw or []:
        value = str(entry or "").strip().lower()
        if value:
            vals.append(value)
    return ",".join(vals)


def _parse_roundtime(raw: str) -> tuple[int, str, int]:
    text = str(raw or "").strip()
    if not text:
        return 0, "fixed", 0
    upper = text.upper()
    if upper == "VARIES":
        return 0, "varies", 0
    if upper == "ATTACK":
        return 0, "attack", 0
    match = re.fullmatch(r"ATTACK\s*([+-]\s*\d+)?", upper)
    if match:
        mod = match.group(1) or ""
        mod = int(mod.replace(" ", "")) if mod else 0
        return 0, "attack", mod
    match = re.fullmatch(r"(\d+)S", upper)
    if match:
        return int(match.group(1)), "fixed", 0
    match = re.search(r"(\d+)", upper)
    if match:
        return int(match.group(1)), "fixed", 0
    return 0, "fixed", 0


def _parse_stamina(raw) -> tuple[int, int]:
    text = str(raw or "").strip()
    if not text:
        return 0, 0
    numbers = [int(value) for value in re.findall(r"\d+", text)]
    if not numbers:
        return 0, 0
    if "minimum" in text.lower() and "maximum" in text.lower() and len(numbers) >= 2:
        return min(numbers[0], numbers[1]), max(numbers[0], numbers[1])
    if len(numbers) >= 2 and "per round" in text.lower():
        return numbers[0], numbers[0] + numbers[1]
    return numbers[0], numbers[0]


def sync_combat_maneuvers(db, defs: dict) -> int:
    """Upsert combat maneuver registry rows from Lua definitions."""
    if not db or not defs:
        return 0

    synced = 0
    for mnemonic, meta in sorted(defs.items()):
        if str(mnemonic).startswith("_") or not isinstance(meta, dict):
            continue

        canonical = str(meta.get("mnemonic") or mnemonic).strip().lower()
        raw_type = str(meta.get("raw_type") or meta.get("type") or "").strip()
        raw_category = str(meta.get("raw_category") or meta.get("category") or "").strip()
        rank_costs = [int(value or 0) for value in (meta.get("rank_costs") or [])]
        while len(rank_costs) < 5:
            rank_costs.append(0)

        base_rt, rt_mode, rt_mod = _parse_roundtime(meta.get("roundtime"))
        stamina_min, stamina_max = _parse_stamina(meta.get("stamina"))
        available_to = _normalize_professions(meta.get("available_to"))

        db.execute_update(
            """
            INSERT INTO combat_maneuvers (
                mnemonic, name, maneuver_type, category_key, raw_category, raw_type,
                is_guild_skill, is_learnable, max_rank,
                rank1_cost, rank2_cost, rank3_cost, rank4_cost, rank5_cost,
                base_roundtime, roundtime_mode, roundtime_modifier, raw_roundtime,
                stamina_cost_min, stamina_cost_max, raw_stamina,
                offensive_gear, requirements, available_to, description,
                mechanics_notes, handler_key
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s
            )
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                maneuver_type = VALUES(maneuver_type),
                category_key = VALUES(category_key),
                raw_category = VALUES(raw_category),
                raw_type = VALUES(raw_type),
                is_guild_skill = VALUES(is_guild_skill),
                is_learnable = VALUES(is_learnable),
                max_rank = VALUES(max_rank),
                rank1_cost = VALUES(rank1_cost),
                rank2_cost = VALUES(rank2_cost),
                rank3_cost = VALUES(rank3_cost),
                rank4_cost = VALUES(rank4_cost),
                rank5_cost = VALUES(rank5_cost),
                base_roundtime = VALUES(base_roundtime),
                roundtime_mode = VALUES(roundtime_mode),
                roundtime_modifier = VALUES(roundtime_modifier),
                raw_roundtime = VALUES(raw_roundtime),
                stamina_cost_min = VALUES(stamina_cost_min),
                stamina_cost_max = VALUES(stamina_cost_max),
                raw_stamina = VALUES(raw_stamina),
                offensive_gear = VALUES(offensive_gear),
                requirements = VALUES(requirements),
                available_to = VALUES(available_to),
                description = VALUES(description),
                mechanics_notes = VALUES(mechanics_notes),
                handler_key = VALUES(handler_key)
            """,
            (
                canonical,
                str(meta.get("name") or canonical),
                _normalize_type(meta.get("type")),
                _normalize_category(meta.get("category")),
                raw_category or None,
                raw_type or None,
                1 if meta.get("is_guild_skill") else 0,
                1 if meta.get("is_learnable", True) else 0,
                int(meta.get("max_rank") or max(1, sum(1 for value in rank_costs if value > 0)) or 1),
                rank_costs[0],
                rank_costs[1],
                rank_costs[2],
                rank_costs[3],
                rank_costs[4],
                base_rt,
                rt_mode,
                rt_mod,
                str(meta.get("roundtime") or ""),
                stamina_min,
                stamina_max,
                str(meta.get("stamina") or ""),
                str(meta.get("offensive_gear") or ""),
                str(meta.get("requirements") or ""),
                available_to,
                str(meta.get("description") or ""),
                str(meta.get("mechanics") or ""),
                str(meta.get("handler_key") or ""),
            ),
        )
        synced += 1

    return synced
