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


def _iter_level_rows(value):
    """
    Iterate sparse Lua level tables safely after lua_to_python() conversion.

    Sparse integer-keyed Lua tables like {[10] = {...}, [15] = {...}} currently
    arrive as Python lists with None holes because the bridge preserves integer
    indices as a 1-based array shape.  Accept both dict and list forms here.
    """
    if isinstance(value, dict):
        for level_key, entries in value.items():
            try:
                yield int(level_key), entries
            except Exception:
                continue
        return
    if isinstance(value, list):
        for idx, entries in enumerate(value, start=1):
            if entries is None:
                continue
            yield idx, entries


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

        for level, entries in _iter_level_rows(data.get("general") or {}):
            parsed = [entry for entry in (_load_entry(row) for row in _as_list(entries)) if entry]
            if parsed:
                out["general"][level] = parsed

        for prof_name, levels in (data.get("profession") or {}).items():
            prof_key = str(prof_name or "").strip()
            if not prof_key:
                continue
            prof_rows = {}
            for level, entries in _iter_level_rows(levels):
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
