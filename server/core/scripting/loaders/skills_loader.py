"""
skills_loader.py
----------------
Loads skill definitions from scripts/data/skills.lua.

Returns a dict with keys:
  "skill_names"    - {skill_id: "Name"}
  "skill_aliases"  - {"abbrev": skill_id}
  "skill_costs"    - {skill_id: {prof_id: (ptp, mtp)}}
  "train_limits"   - {skill_id: {prof_id: max_per_level}}
  "categories"     - {"Category": [skill_id, ...]}

Raises RuntimeError if Lua unavailable or load fails.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def _iter_lua_table(value):
    """
    Accept either Lua hash tables (converted to dict) or sequential Lua arrays
    (converted to list) from lua_to_python().
    """
    if isinstance(value, dict):
        return value.items()
    if isinstance(value, list):
        return enumerate(value, start=1)
    return ()


def load_skills(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("skills_loader: Lua engine not available. Check lupa installation and scripts path.")
    try:
        data = lua_engine.load_data("data/skills")
        if not data:
            raise RuntimeError("skills_loader: Lua returned no data. Check scripts/data/ for errors.")

        skill_names  = {}
        skill_aliases = {}
        skill_costs  = {}
        train_limits = {}
        categories   = {}

        for k, v in _iter_lua_table(data.get("names") or {}):
            skill_names[int(k)] = str(v)

        for k, v in _iter_lua_table(data.get("aliases") or {}):
            skill_aliases[str(k)] = int(v)

        for sid, prof_map in _iter_lua_table(data.get("costs") or {}):
            sid = int(sid)
            skill_costs[sid] = {}
            for pid, cost_pair in _iter_lua_table(prof_map):
                pid = int(pid)
                if isinstance(cost_pair, list) and len(cost_pair) >= 2:
                    skill_costs[sid][pid] = (int(cost_pair[0]), int(cost_pair[1]))

        for sid, prof_map in _iter_lua_table(data.get("train_limits") or {}):
            sid = int(sid)
            train_limits[sid] = {}
            for pid, limit in _iter_lua_table(prof_map):
                train_limits[sid][int(pid)] = int(limit)

        for cat, skill_list in _iter_lua_table(data.get("categories") or {}):
            if isinstance(skill_list, list):
                categories[str(cat)] = [int(x) for x in skill_list]

        log.info("skills_loader: loaded %d skills from Lua", len(skill_names))
        return {
            "skill_names":   skill_names,
            "skill_aliases": skill_aliases,
            "skill_costs":   skill_costs,
            "train_limits":  train_limits,
            "categories":    categories,
        }
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("skills_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"skills_loader: Lua load failed — {e}") from e
