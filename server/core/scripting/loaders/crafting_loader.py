"""
crafting_loader.py
------------------
Loads shared Artisan Guild / crafting definitions from scripts/data/crafting.lua.

Returns a dict with keys:
  "total_rank_limit"
  "rank_bands"
  "skill_order"
  "skills"
  "stations"
  "recipes"
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def _iter_lua_table(value):
    if isinstance(value, dict):
        return value.items()
    if isinstance(value, list):
        return enumerate(value, start=1)
    return ()


def _as_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [v for _, v in sorted(value.items(), key=lambda kv: int(kv[0]))]
    return []


def load_crafting(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("crafting_loader: Lua engine not available. Check lupa installation and scripts path.")
    try:
        data = lua_engine.load_data("data/crafting")
        if not data:
            raise RuntimeError("crafting_loader: Lua returned no data. Check scripts/data/ for errors.")

        out = {
            "total_rank_limit": int(data.get("total_rank_limit") or 1200),
            "rank_bands": [],
            "skill_order": [],
            "skills": {},
            "stations": {},
            "recipes": {},
        }

        for band in _as_list(data.get("rank_bands") or []):
            if not isinstance(band, dict):
                continue
            out["rank_bands"].append({
                "key": str(band.get("key") or "").strip(),
                "label": str(band.get("label") or "").strip(),
                "min": int(band.get("min") or 0),
                "max": int(band.get("max") or 0),
            })

        for entry in _as_list(data.get("skill_order") or []):
            if entry:
                out["skill_order"].append(str(entry).strip())

        for key, skill in _iter_lua_table(data.get("skills") or {}):
            if not isinstance(skill, dict):
                continue
            out["skills"][str(key)] = {
                "key": str(skill.get("key") or key).strip(),
                "label": str(skill.get("label") or key).strip(),
                "command_token": str(skill.get("command_token") or key).strip(),
                "family": str(skill.get("family") or "").strip(),
                "retail_group": str(skill.get("retail_group") or "").strip(),
                "weapon_group": str(skill.get("weapon_group") or "").strip(),
            }

        for key, station in _iter_lua_table(data.get("stations") or {}):
            if not isinstance(station, dict):
                continue
            out["stations"][str(key)] = {
                "key": str(station.get("key") or key).strip(),
                "label": str(station.get("label") or key).strip(),
                "skills": [str(v).strip() for v in _as_list(station.get("skills") or []) if str(v).strip()],
                "room_tags": [str(v).strip() for v in _as_list(station.get("room_tags") or []) if str(v).strip()],
            }

        for key, recipe in _iter_lua_table(data.get("recipes") or {}):
            if not isinstance(recipe, dict):
                continue
            materials = []
            tools = []
            stages = []
            for mat in _as_list(recipe.get("materials") or []):
                if not isinstance(mat, dict):
                    continue
                materials.append({
                    "key": str(mat.get("key") or "").strip(),
                    "count": int(mat.get("count") or 0),
                    "label": str(mat.get("label") or mat.get("key") or "").strip(),
                    "consume": bool(mat.get("consume", True)),
                })
            for tool in _as_list(recipe.get("tools") or []):
                if not isinstance(tool, dict):
                    continue
                tools.append({
                    "key": str(tool.get("key") or "").strip(),
                    "label": str(tool.get("label") or tool.get("key") or "").strip(),
                })
            for stage in _as_list(recipe.get("stages") or []):
                if not isinstance(stage, dict):
                    continue
                stages.append({
                    "key": str(stage.get("key") or "").strip(),
                    "label": str(stage.get("label") or stage.get("key") or "").strip(),
                    "command": str(stage.get("command") or "").strip(),
                })
            item_keys = {}
            for item_key, value in _iter_lua_table(recipe.get("item_keys") or {}):
                value_str = str(value or "").strip()
                if value_str:
                    item_keys[str(item_key)] = value_str
            out["recipes"][str(key)] = {
                "key": str(recipe.get("key") or key).strip(),
                "label": str(recipe.get("label") or key).strip(),
                "skill": str(recipe.get("skill") or "").strip(),
                "station": str(recipe.get("station") or "").strip(),
                "output_noun": str(recipe.get("output_noun") or "").strip(),
                "output_item_short_name": str(recipe.get("output_item_short_name") or "").strip(),
                "difficulty": str(recipe.get("difficulty") or "").strip(),
                "rank_projects": int(recipe.get("rank_projects") or 1),
                "rough_yield_min": int(recipe.get("rough_yield_min") or 1),
                "rough_yield_max": int(recipe.get("rough_yield_max") or recipe.get("rough_yield_min") or 1),
                "item_keys": item_keys,
                "tools": tools,
                "materials": materials,
                "stages": stages,
            }

        log.info(
            "crafting_loader: loaded %d artisan skills, %d stations, %d recipes from Lua",
            len(out["skills"]), len(out["stations"]), len(out["recipes"])
        )
        return out
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("crafting_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"crafting_loader: Lua load failed — {e}") from e
