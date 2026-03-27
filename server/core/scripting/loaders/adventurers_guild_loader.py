"""
adventurers_guild_loader.py
---------------------------
Loads Adventurer's Guild authority, rank, and bounty definitions from Lua.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def _iter_table(value):
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


def load_adventurers_guild(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("adventurers_guild_loader: Lua engine not available.")
    try:
        data = lua_engine.load_data("data/adventurers_guild")
        if not data:
            raise RuntimeError("adventurers_guild_loader: Lua returned no data.")

        out = {
            "rank_thresholds": [],
            "authorities": {},
            "bounties": {},
        }

        for row in _as_list(data.get("rank_thresholds") or []):
            if not isinstance(row, dict):
                continue
            out["rank_thresholds"].append({
                "points": int(row.get("points") or 0),
                "rank": int(row.get("rank") or 1),
                "title": str(row.get("title") or "Associate").strip(),
            })
        out["rank_thresholds"].sort(key=lambda r: int(r["points"]))

        for key, row in _iter_table(data.get("authorities") or {}):
            if not isinstance(row, dict):
                continue
            template_id = str(row.get("template_id") or key).strip()
            out["authorities"][template_id] = {
                "template_id": template_id,
                "town_name": str(row.get("town_name") or "").strip(),
                "room_id": int(row.get("room_id") or 0),
                "role": str(row.get("role") or "taskmaster").strip(),
            }

        for town_name, entries in _iter_table(data.get("bounties") or {}):
            clean = []
            for row in _as_list(entries):
                if not isinstance(row, dict):
                    continue
                clean.append({
                    "key": str(row.get("key") or "").strip(),
                    "type": str(row.get("type") or "cull").strip().lower(),
                    "min_level": int(row.get("min_level") or 1),
                    "max_level": int(row.get("max_level") or 100),
                    "target_template_id": str(row.get("target_template_id") or "").strip(),
                    "target_name": str(row.get("target_name") or "").strip(),
                    "target_count": int(row.get("target_count") or 1),
                    "reward_silver": int(row.get("reward_silver") or 0),
                    "reward_experience": int(row.get("reward_experience") or 0),
                    "reward_fame": int(row.get("reward_fame") or 0),
                    "reward_points": int(row.get("reward_points") or 0),
                    "area": str(row.get("area") or "").strip(),
                })
            out["bounties"][str(town_name)] = clean

        log.info(
            "adventurers_guild_loader: loaded %d authorities and %d town bounty pools",
            len(out["authorities"]), len(out["bounties"])
        )
        return out
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("adventurers_guild_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"adventurers_guild_loader: Lua load failed — {e}") from e
