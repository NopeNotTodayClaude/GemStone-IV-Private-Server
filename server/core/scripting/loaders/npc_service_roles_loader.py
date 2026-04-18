"""
npc_service_roles_loader.py
---------------------------
Loads scripts/data/npc_services.lua into a normalized Python dict.
"""

import logging

log = logging.getLogger(__name__)


def _to_str_list(values):
    if isinstance(values, (list, tuple)):
        return [str(v).strip() for v in values if str(v).strip()]
    if values is None:
        return []
    text = str(values).strip()
    return [text] if text else []


def load_npc_service_roles(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        log.warning("npc_service_roles_loader: Lua engine unavailable")
        return {"templates": {}}

    try:
        data = lua_engine.load_data("data/npc_services") or {}
        if not isinstance(data, dict):
            raise RuntimeError("npc_services.lua did not return a dict")

        templates = {}
        for template_id, raw in (data.get("templates") or {}).items():
            if not isinstance(raw, dict):
                continue
            tid = str(template_id or "").strip()
            if not tid:
                continue
            templates[tid] = {
                "role": str(raw.get("role") or "").strip(),
                "service_tags": [tag.lower() for tag in _to_str_list(raw.get("service_tags"))],
                "lua_context": dict(raw.get("lua_context") or {}),
            }

        log.info("npc_service_roles_loader: loaded %d explicit npc service templates", len(templates))
        return {"templates": templates}
    except Exception as e:
        log.error("npc_service_roles_loader: failed to load npc services (%s)", e, exc_info=True)
        return {"templates": {}}
