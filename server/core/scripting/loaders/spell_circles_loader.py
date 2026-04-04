"""
spell_circles_loader.py
-----------------------
Loads scripts/globals/magic/spell_circles.lua for player-facing spell-circle
metadata used by training and spellbook systems.
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


def load_spell_circles(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("spell_circles_loader: Lua engine not available. Check lupa installation and scripts path.")
    try:
        data = lua_engine.load_data("globals/magic/spell_circles")
        if not data:
            raise RuntimeError("spell_circles_loader: Lua returned no data. Check scripts/globals/magic/spell_circles.lua.")

        circles = {}
        for circle_id, raw_circle in _iter_lua_table(data.get("circles") or {}):
            if not isinstance(raw_circle, dict):
                continue
            cid = int(circle_id)
            circles[cid] = {
                "id": cid,
                "name": str(raw_circle.get("name") or f"Circle {cid}"),
                "abbrev": str(raw_circle.get("abbrev") or ""),
                "sphere": str(raw_circle.get("sphere") or ""),
                "prefix": int(raw_circle.get("prefix", 0) or 0),
                "cs_stat": str(raw_circle.get("cs_stat") or ""),
                "td_stat": str(raw_circle.get("td_stat") or ""),
                "is_trainable": bool(raw_circle.get("is_trainable", False)),
            }

        profession_circles = {}
        for prof_id, raw_list in _iter_lua_table(data.get("profession_circles") or {}):
            circles_list = []
            for circle_id in raw_list or []:
                try:
                    circles_list.append(int(circle_id))
                except Exception:
                    continue
            profession_circles[int(prof_id)] = circles_list

        log.info("spell_circles_loader: loaded %d circles from Lua", len(circles))
        return {
            "circles": circles,
            "profession_circles": profession_circles,
        }
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("spell_circles_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"spell_circles_loader: Lua load failed — {e}") from e
