"""
quest_npc_binding_loader.py
---------------------------
Loads quest-facing NPC room bindings from scripts/quests/**/*.lua so quest Lua
stays authoritative for start/turn-in placement metadata.
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
            yield os.path.splitext(rel_path)[0].replace("\\", "/")


def _coerce_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _as_table_list(value) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        def _sort_key(item):
            raw_key = item[0]
            try:
                return (0, int(raw_key))
            except (TypeError, ValueError):
                return (1, str(raw_key))

        return [row for _, row in sorted(value.items(), key=_sort_key)]
    if value is None:
        return []
    return [value]


def _as_template_ids(value) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in _as_table_list(value):
        text = str(raw or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _bind_room(binding_map: dict[str, int], source_map: dict[str, str], template_id: str, room_id: int, module_path: str):
    template_id = str(template_id or "").strip()
    room_id = _coerce_int(room_id, 0)
    if not template_id or room_id <= 0:
        return

    existing = binding_map.get(template_id)
    if existing and existing != room_id:
        log.warning(
            "quest_npc_binding_loader: conflicting room bindings for %s (%s in %s vs %s in %s)",
            template_id,
            existing,
            source_map.get(template_id, "unknown"),
            room_id,
            module_path,
        )
        return

    binding_map[template_id] = room_id
    source_map[template_id] = module_path


def load_quest_npc_metadata(lua_engine, scripts_path: str) -> dict[str, object]:
    """Load authoritative quest-facing NPC metadata from Lua."""
    if not lua_engine or not lua_engine.available:
        return {"bindings": {}, "template_ids": set()}

    bindings: dict[str, int] = {}
    sources: dict[str, str] = {}
    template_ids: set[str] = set()

    for module_path in _iter_quest_modules(scripts_path) or ():
        try:
            data = lua_engine.load_data(module_path)
        except Exception as e:
            log.error("quest_npc_binding_loader: failed to load %s: %s", module_path, e)
            continue

        if not isinstance(data, dict) or not data:
            continue
        if bool(data.get("disabled")) or data.get("enabled") is False:
            continue

        start_room_id = _coerce_int(data.get("start_room_id"), 0)
        turnin_room_id = _coerce_int(
            data.get("turnin_room_id", data.get("completion_room_id", data.get("report_room_id"))),
            0,
        )
        start_ids = _as_template_ids(data.get("start_npc_template_ids", data.get("start_npc_template_id")))
        turnin_ids = _as_template_ids(data.get("turnin_npc_template_ids", data.get("turnin_npc_template_id")))
        template_ids.update(start_ids)
        template_ids.update(turnin_ids)

        for template_id in start_ids:
            _bind_room(bindings, sources, template_id, start_room_id, module_path)

        for template_id in turnin_ids:
            _bind_room(bindings, sources, template_id, turnin_room_id, module_path)

        if start_room_id > 0 and start_ids:
            start_set = set(start_ids)
            for template_id in turnin_ids:
                if template_id in start_set:
                    _bind_room(bindings, sources, template_id, start_room_id, module_path)

    log.info(
        "quest_npc_binding_loader: loaded %d quest NPC room bindings across %d quest NPCs",
        len(bindings),
        len(template_ids),
    )
    return {"bindings": bindings, "template_ids": template_ids}


def load_quest_npc_bindings(lua_engine, scripts_path: str) -> dict[str, int]:
    """Load quest start/turn-in NPC room bindings from Lua."""
    return dict(load_quest_npc_metadata(lua_engine, scripts_path).get("bindings") or {})


def load_quest_npc_template_ids(lua_engine, scripts_path: str) -> set[str]:
    """Load the set of NPC template ids referenced by quest Lua."""
    return set(load_quest_npc_metadata(lua_engine, scripts_path).get("template_ids") or set())
