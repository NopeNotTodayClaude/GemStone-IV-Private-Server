"""
quest_definition_loader.py
--------------------------
Scans scripts/quests/**/*.lua, loads each quest table through the Lua engine,
and keeps quest_definitions in sync so Lua remains the source of truth.
"""

from __future__ import annotations

import logging
import os

log = logging.getLogger(__name__)


def _iter_quest_modules(scripts_path: str):
    quests_path = os.path.join(scripts_path, "quests")
    if not os.path.isdir(quests_path):
        return
    for root, dirnames, filenames in os.walk(quests_path):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("_"))
        for fname in sorted(filenames):
            if not fname.endswith(".lua"):
                continue
            if fname == "quest_template.lua":
                continue
            abs_path = os.path.join(root, fname)
            rel_path = os.path.relpath(abs_path, scripts_path)
            module_path = os.path.splitext(rel_path)[0].replace("\\", "/")
            yield module_path


def _coerce_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def load_quest_definitions(lua_engine, scripts_path: str) -> list[dict]:
    """Load all Lua quest definitions from scripts/quests."""
    if not lua_engine or not lua_engine.available:
        return []

    rows_by_key: dict[str, dict] = {}
    for module_path in _iter_quest_modules(scripts_path) or ():
        try:
            data = lua_engine.load_data(module_path)
        except Exception as e:
            log.error("quest_definition_loader: failed to load %s: %s", module_path, e)
            continue
        if not isinstance(data, dict) or not data:
            log.warning("quest_definition_loader: %s returned no quest table", module_path)
            continue
        if bool(data.get("disabled")) or data.get("enabled") is False:
            log.info("quest_definition_loader: skipping disabled quest %s", module_path)
            continue

        key_name = str(data.get("key_name") or "").strip().lower()
        if not key_name:
            log.warning("quest_definition_loader: %s missing Quest.key_name", module_path)
            continue
        existing = rows_by_key.get(key_name)
        if existing:
            log.warning(
                "quest_definition_loader: duplicate Quest.key_name '%s' in %s overrides %s",
                key_name,
                module_path,
                existing.get("lua_script"),
            )

        title = str(data.get("title") or key_name.replace("_", " ").title()).strip()
        description = str(data.get("description") or title).strip()
        min_level = _coerce_int(data.get("min_level", data.get("level_req", 1)), 1)
        max_level = _coerce_int(data.get("max_level", 100), 100)
        if max_level < min_level:
            max_level = min_level

        rows_by_key[key_name] = {
            "key_name": key_name,
            "title": title,
            "description": description,
            "min_level": min_level,
            "max_level": max_level,
            "is_repeatable": 1 if data.get("repeatable") else 0,
            "lua_script": module_path,
        }

    rows = [rows_by_key[key] for key in sorted(rows_by_key)]
    log.info("quest_definition_loader: loaded %d quest definitions from Lua", len(rows))
    return rows


def sync_quest_definitions(db, defs: list[dict]) -> int:
    """Upsert quest_definitions rows from Lua metadata."""
    if not db or not defs:
        return 0

    synced = 0
    for row in defs:
        db.execute_update(
            """
            INSERT INTO quest_definitions (
                key_name, title, description, min_level, max_level, is_repeatable, lua_script
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                description = VALUES(description),
                min_level = VALUES(min_level),
                max_level = VALUES(max_level),
                is_repeatable = VALUES(is_repeatable),
                lua_script = VALUES(lua_script)
            """,
            (
                row["key_name"],
                row["title"],
                row["description"],
                int(row["min_level"]),
                int(row["max_level"]),
                int(row["is_repeatable"]),
                row["lua_script"],
            ),
        )
        synced += 1

    return synced
