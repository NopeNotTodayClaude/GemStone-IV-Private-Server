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
            "towns": {},
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

        for town_name, row in _iter_table(data.get("towns") or {}):
            if not isinstance(row, dict):
                continue
            out["towns"][str(town_name)] = {
                "taskmaster": str(row.get("taskmaster") or "").strip(),
                "taskmaster_room_id": int(row.get("taskmaster_room_id") or 0),
                "clerk": str(row.get("clerk") or "").strip(),
                "clerk_room_id": int(row.get("clerk_room_id") or 0),
                "bounty_room_ids": [int(v) for v in _as_list(row.get("bounty_room_ids") or []) if str(v).strip()],
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
                    "target_item_type": str(row.get("target_item_type") or "").strip(),
                    "target_short_names": _as_list(row.get("target_short_names") or []),
                    "target_nouns": _as_list(row.get("target_nouns") or []),
                    "search_zone_names": _as_list(row.get("search_zone_names") or []),
                    "search_room_ids": [int(v) for v in _as_list(row.get("search_room_ids") or []) if str(v).strip()],
                    "found_item_name": str(row.get("found_item_name") or "").strip(),
                    "found_item_short_name": str(row.get("found_item_short_name") or "").strip(),
                    "found_item_noun": str(row.get("found_item_noun") or "").strip(),
                    "destination_room_id": int(row.get("destination_room_id") or 0),
                    "destination_name": str(row.get("destination_name") or "").strip(),
                    "report_room_id": int(row.get("report_room_id") or 0),
                })
            out["bounties"][str(town_name)] = clean

        log.info(
            "adventurers_guild_loader: loaded %d authorities, %d towns, and %d town bounty pools",
            len(out["authorities"]), len(out["towns"]), len(out["bounties"])
        )
        return out
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("adventurers_guild_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"adventurers_guild_loader: Lua load failed — {e}") from e
