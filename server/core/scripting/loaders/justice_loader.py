"""
justice_loader.py
-----------------
Loads scripts/data/justice.lua into a normalized Python dict.
"""

import logging

log = logging.getLogger(__name__)


def _to_int(value, default=0):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return int(default)


def _to_str_list(values):
    if isinstance(values, (list, tuple)):
        return [str(v).strip() for v in values if str(v).strip()]
    if values is None:
        return []
    text = str(values).strip()
    return [text] if text else []


def _normalize_task(raw: dict) -> dict:
    return {
        "key": str(raw.get("key") or "").strip().lower(),
        "label": str(raw.get("label") or "").strip(),
        "room_id": _to_int(raw.get("room_id"), 0),
        "object_name": str(raw.get("object_name") or "").strip().lower(),
        "briefing": str(raw.get("briefing") or "").strip(),
        "inspect_intro": str(raw.get("inspect_intro") or "").strip(),
        "sequence": [str(v).strip().lower() for v in (raw.get("sequence") or []) if str(v).strip()],
        "completion_text": str(raw.get("completion_text") or "").strip(),
        "cycles_required": max(1, _to_int(raw.get("cycles_required"), 1)),
    }


def load_justice(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        log.warning("justice_loader: Lua engine unavailable")
        return {
            "config": {},
            "charge_defs": {},
            "question_sets": {},
            "service_verbs": {},
            "jurisdictions": {},
            "npcs": {},
        }

    try:
        data = lua_engine.load_data("data/justice") or {}
        if not isinstance(data, dict):
            raise RuntimeError("justice.lua did not return a dict")

        config = dict(data.get("config") or {})
        charge_defs = {}
        question_sets = {}
        service_verbs = {}
        jurisdictions = {}
        npcs = {}

        for charge_code, raw in (data.get("charge_defs") or {}).items():
            if not isinstance(raw, dict):
                continue
            code = str(charge_code or "").strip().lower()
            if not code:
                continue
            charge_defs[code] = {
                "code": code,
                "label": str(raw.get("label") or code.replace("_", " ").title()).strip(),
                "accusable": bool(raw.get("accusable", False)),
                "severity": max(1, _to_int(raw.get("severity"), 1)),
                "fine": max(0, _to_int(raw.get("fine"), 0)),
                "incarceration_min": max(0, _to_int(raw.get("incarceration_min"), 0)),
                "service_min": max(0, _to_int(raw.get("service_min"), 0)),
                "allow_service": bool(raw.get("allow_service", True)),
                "banishment_days": max(0, _to_int(raw.get("banishment_days"), 0)),
            }

        for set_key, raw_rows in (data.get("question_sets") or {}).items():
            rows = []
            for raw in raw_rows or []:
                if not isinstance(raw, dict):
                    continue
                qkey = str(raw.get("key") or "").strip().lower()
                prompt = str(raw.get("prompt") or "").strip()
                if qkey and prompt:
                    rows.append({"key": qkey, "prompt": prompt})
            if rows:
                question_sets[str(set_key or "").strip().lower()] = rows

        for verb_key, raw in (data.get("service_verbs") or {}).items():
            key = str(verb_key or "").strip().lower()
            if not key:
                continue
            if isinstance(raw, dict):
                service_verbs[key] = {
                    "key": key,
                    "label": str(raw.get("label") or key.upper()).strip(),
                }
            else:
                service_verbs[key] = {"key": key, "label": key.upper()}

        for jurisdiction_id, raw in (data.get("jurisdictions") or {}).items():
            if not isinstance(raw, dict):
                continue
            jid = str(jurisdiction_id or "").strip().lower()
            if not jid:
                continue
            tasks = []
            for task_raw in raw.get("service_tasks") or []:
                if not isinstance(task_raw, dict):
                    continue
                task = _normalize_task(task_raw)
                if task["key"] and task["room_id"] > 0 and task["object_name"] and task["sequence"]:
                    tasks.append(task)
            jurisdictions[jid] = {
                "id": jid,
                "display_name": str(raw.get("display_name") or jid.replace("_", " ").title()).strip(),
                "aliases": [alias.lower() for alias in _to_str_list(raw.get("aliases"))],
                "zone_aliases": [alias.lower() for alias in _to_str_list(raw.get("zone_aliases"))],
                "courtroom_room_id": _to_int(raw.get("courtroom_room_id"), 0),
                "clerk_room_id": _to_int(raw.get("clerk_room_id"), 0),
                "jail_room_id": _to_int(raw.get("jail_room_id"), 0),
                "stockade_room_id": _to_int(raw.get("stockade_room_id"), 0),
                "pit_room_id": _to_int(raw.get("pit_room_id"), 0),
                "release_room_id": _to_int(raw.get("release_room_id"), 0),
                "room_ids": [_to_int(v, 0) for v in (raw.get("room_ids") or []) if _to_int(v, 0) > 0],
                "service_tasks": tasks,
            }

        for template_id, raw in (data.get("npcs") or {}).items():
            if not isinstance(raw, dict):
                continue
            tid = str(template_id or "").strip()
            room_id = _to_int(raw.get("room_id"), 0)
            if not tid or room_id <= 0:
                continue
            npcs[tid] = dict(raw)
            npcs[tid]["service_tags"] = _to_str_list(raw.get("service_tags"))
            npcs[tid]["lua_context"] = dict(raw.get("lua_context") or {})
            npcs[tid]["justice_role"] = str(raw.get("justice_role") or "").strip().lower()
            npcs[tid]["justice_jurisdiction"] = str(raw.get("justice_jurisdiction") or "").strip().lower()

        log.info(
            "justice_loader: loaded %d jurisdictions, %d charge defs, %d NPC templates",
            len(jurisdictions),
            len(charge_defs),
            len(npcs),
        )
        return {
            "config": config,
            "charge_defs": charge_defs,
            "question_sets": question_sets,
            "service_verbs": service_verbs,
            "jurisdictions": jurisdictions,
            "npcs": npcs,
        }
    except Exception as e:
        log.error("justice_loader: failed to load justice.lua (%s)", e, exc_info=True)
        return {
            "config": {},
            "charge_defs": {},
            "question_sets": {},
            "service_verbs": {},
            "jurisdictions": {},
            "npcs": {},
        }
