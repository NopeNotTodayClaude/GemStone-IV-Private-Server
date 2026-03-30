"""
weapon_techniques_loader.py
---------------------------
Loads scripts/weapon_techniques/definitions.lua and keeps the SQL metadata
table in sync so Lua stays the source of truth.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


_CATEGORY_TO_SKILL_NAME = {
    "edged": "Edged Weapons",
    "blunt": "Blunt Weapons",
    "twohanded": "Two-Handed Weapons",
    "ranged": "Ranged Weapons",
    "polearm": "Polearm Weapons",
    "brawling": "Brawling",
}


def load_weapon_techniques(engine) -> dict:
    """Load scripts/weapon_techniques/definitions.lua and return a Python dict."""
    if not engine or not engine.available:
        return None
    try:
        data = engine.require("weapon_techniques/definitions")
        data = engine.lua_to_python(data) if data else None
        if isinstance(data, dict) and data:
            log.info("weapon_techniques_loader: loaded %d technique defs", len(data))
            return data
        log.warning("weapon_techniques_loader: empty or invalid technique defs")
        return None
    except Exception as e:
        log.error("weapon_techniques_loader: failed to load definitions.lua: %s", e, exc_info=True)
        return None


def sync_weapon_techniques(db, defs: dict) -> int:
    """
    Upsert weapon_techniques rows from Lua definitions.
    Returns number of synced technique records.
    """
    if not db or not defs:
        return 0

    rows = db.get_skills() or []
    skill_name_to_id = {
        str(row.get("name") or "").strip().lower(): int(row.get("id") or 0)
        for row in rows
        if int(row.get("id") or 0) in (5, 6, 7, 8, 10, 11)
    }

    synced = 0
    for mnemonic, tech in sorted(defs.items()):
        if not isinstance(tech, dict):
            continue
        category = str(tech.get("category") or "").strip().lower()
        skill_name = _CATEGORY_TO_SKILL_NAME.get(category, "")
        skill_id = int(skill_name_to_id.get(skill_name.lower(), 0) or 0)
        if not skill_id:
            log.warning("weapon_techniques_loader: no skill id for %s (%s)", mnemonic, category)
            continue

        thresholds = list(tech.get("rank_thresholds") or [])
        while len(thresholds) < 5:
            thresholds.append(thresholds[-1] if thresholds else 0)

        available_to = ",".join(str(x).strip().lower() for x in (tech.get("available_to") or []) if str(x).strip())
        db.execute_update(
            """
            INSERT INTO weapon_techniques (
                mnemonic, name, weapon_category, technique_type, weapon_skill_id,
                min_skill_ranks, rank2_ranks, rank3_ranks, rank4_ranks, rank5_ranks,
                stamina_cost, base_roundtime, cooldown_seconds, description,
                mechanics_notes, available_to, reaction_trigger, offensive_gear,
                flares_enabled, racial_size_mod, target_stance_bonus, shield_def_bonus
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                weapon_category = VALUES(weapon_category),
                technique_type = VALUES(technique_type),
                weapon_skill_id = VALUES(weapon_skill_id),
                min_skill_ranks = VALUES(min_skill_ranks),
                rank2_ranks = VALUES(rank2_ranks),
                rank3_ranks = VALUES(rank3_ranks),
                rank4_ranks = VALUES(rank4_ranks),
                rank5_ranks = VALUES(rank5_ranks),
                stamina_cost = VALUES(stamina_cost),
                base_roundtime = VALUES(base_roundtime),
                cooldown_seconds = VALUES(cooldown_seconds),
                description = VALUES(description),
                mechanics_notes = VALUES(mechanics_notes),
                available_to = VALUES(available_to),
                reaction_trigger = VALUES(reaction_trigger),
                offensive_gear = VALUES(offensive_gear),
                flares_enabled = VALUES(flares_enabled),
                racial_size_mod = VALUES(racial_size_mod),
                target_stance_bonus = VALUES(target_stance_bonus),
                shield_def_bonus = VALUES(shield_def_bonus)
            """,
            (
                mnemonic,
                str(tech.get("name") or mnemonic),
                category,
                str(tech.get("type") or "").strip().lower(),
                skill_id,
                int(tech.get("min_ranks") or thresholds[0] or 0),
                int(thresholds[1] or 0),
                int(thresholds[2] or 0),
                int(thresholds[3] or 0),
                int(thresholds[4] or 0),
                int(tech.get("stamina_cost") or 0),
                int(tech.get("base_rt") or 0),
                int(tech.get("cooldown") or 0),
                str(tech.get("description") or ""),
                "",
                available_to,
                str(tech.get("reaction_trigger") or "") or None,
                str(tech.get("offensive_gear") or "right_hand"),
                1 if tech.get("flares_enabled") else 0,
                1 if tech.get("racial_size_mod") else 0,
                1,
                1,
            ),
        )
        synced += 1

    return synced
