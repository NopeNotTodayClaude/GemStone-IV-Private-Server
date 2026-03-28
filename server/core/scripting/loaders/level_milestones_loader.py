"""
level_milestones_loader.py
--------------------------
Loads Lua-backed level milestone reminder data.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def _as_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [v for _, v in sorted(value.items(), key=lambda kv: int(kv[0]))]
    return []


def _load_entry(row):
    if not isinstance(row, dict):
        return None
    return {
        "kind": str(row.get("kind") or "").strip(),
        "title": str(row.get("title") or "").strip(),
        "text": str(row.get("text") or "").strip(),
        "source": str(row.get("source") or "").strip(),
        "command_hint": str(row.get("command_hint") or "").strip(),
    }


def load_level_milestones(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("level_milestones_loader: Lua engine not available.")
    try:
        data = lua_engine.load_data("data/level_milestones")
        if not data:
            raise RuntimeError("level_milestones_loader: Lua returned no data.")

        out = {"general": {}, "profession": {}}

        for level_key, entries in (data.get("general") or {}).items():
            try:
                level = int(level_key)
            except Exception:
                continue
            parsed = [entry for entry in (_load_entry(row) for row in _as_list(entries)) if entry]
            if parsed:
                out["general"][level] = parsed

        for prof_name, levels in (data.get("profession") or {}).items():
            prof_key = str(prof_name or "").strip()
            if not prof_key or not isinstance(levels, dict):
                continue
            prof_rows = {}
            for level_key, entries in levels.items():
                try:
                    level = int(level_key)
                except Exception:
                    continue
                parsed = [entry for entry in (_load_entry(row) for row in _as_list(entries)) if entry]
                if parsed:
                    prof_rows[level] = parsed
            if prof_rows:
                out["profession"][prof_key] = prof_rows

        log.info(
            "level_milestones_loader: loaded %d general milestone levels and %d profession milestone sets",
            len(out["general"]), len(out["profession"])
        )
        return out
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("level_milestones_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"level_milestones_loader: Lua load failed - {e}") from e
