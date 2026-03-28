"""
skinning_loader.py
------------------
Loads Lua-backed skinning configuration.
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


def load_skinning(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("skinning_loader: Lua engine not available.")
    try:
        data = lua_engine.load_data("data/skinning")
        if not data:
            raise RuntimeError("skinning_loader: Lua returned no data.")

        out = {
            "settings": dict(data.get("settings") or {}),
            "quality_tiers": [],
            "tool_bonuses": {},
            "noun_values": {},
            "noun_difficulty": {},
            "item_overrides": {},
        }

        for row in _as_list(data.get("quality_tiers") or []):
            if not isinstance(row, dict):
                continue
            out["quality_tiers"].append({
                "key": str(row.get("key") or "").strip(),
                "label": str(row.get("label") or row.get("key") or "").strip(),
                "min_margin": int(row.get("min_margin") or 0),
                "value_multiplier": float(row.get("value_multiplier") or 1.0),
            })
        out["quality_tiers"].sort(key=lambda r: int(r["min_margin"]), reverse=True)

        for key, value in (data.get("tool_bonuses") or {}).items():
            out["tool_bonuses"][str(key).strip().lower()] = int(value or 0)

        for key, value in (data.get("noun_values") or {}).items():
            out["noun_values"][str(key).strip().lower()] = int(value or 0)

        for key, value in (data.get("noun_difficulty") or {}).items():
            out["noun_difficulty"][str(key).strip().lower()] = int(value or 0)

        for key, row in (data.get("item_overrides") or {}).items():
            if not isinstance(row, dict):
                continue
            out["item_overrides"][str(key).strip().lower()] = {
                "value": int(row.get("value") or 0),
                "noun": str(row.get("noun") or "").strip().lower(),
                "difficulty": int(row.get("difficulty") or 0),
            }

        log.info(
            "skinning_loader: loaded %d quality tiers and %d item overrides",
            len(out["quality_tiers"]), len(out["item_overrides"])
        )
        return out
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("skinning_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"skinning_loader: Lua load failed — {e}") from e
