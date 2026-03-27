"""
items_loader.py
---------------
Loads all item template data from Lua data files.

Returns per-category lists/dicts matching the format the rest of the server
expects.  Raises RuntimeError on any failure — there are no fallbacks.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def load_weapons(lua_engine) -> Optional[dict]:
    """
    Returns a dict of weapon lists keyed by category:
      { "edged": [...], "blunt": [...], "twohanded": [...],
        "polearm": [...], "ranged": [...], "thrown": [...], "brawling": [...] }
    Raises RuntimeError on failure.
    """
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("items_loader: Lua engine not available — cannot load data")
    try:
        data = lua_engine.load_data("data/items/weapons")
        if not data:
            raise RuntimeError(
                "items_loader: weapons.lua returned no data — check scripts/data/items/weapons.lua"
            )
        result = {}
        for category in ("edged", "blunt", "twohanded", "polearm", "ranged", "thrown", "brawling"):
            raw = data.get(category)
            if isinstance(raw, list):
                result[category] = [_normalise_weapon(w) for w in raw if isinstance(w, dict)]
            else:
                result[category] = []
        total = sum(len(v) for v in result.values())
        log.info("items_loader: loaded %d weapon templates from Lua", total)
        return result
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("items_loader.load_weapons: failed: %s", e, exc_info=True)
        raise RuntimeError(f"items_loader.load_weapons: Lua load failed — {e}") from e


def load_armor(lua_engine) -> Optional[list]:
    """
    Returns a list of armor template dicts.
    Raises RuntimeError on failure.
    """
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("items_loader: Lua engine not available — cannot load data")
    try:
        data = lua_engine.load_data("data/items/armor")
        if not data:
            raise RuntimeError(
                "items_loader: armor.lua returned no data — check scripts/data/items/armor.lua"
            )
        raw = data.get("templates") or []
        if not isinstance(raw, list):
            raise RuntimeError("items_loader: armor.lua 'templates' key is not a list")
        result = [_normalise_armor(a) for a in raw if isinstance(a, dict)]
        log.info("items_loader: loaded %d armor templates from Lua", len(result))
        return result
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("items_loader.load_armor: failed: %s", e, exc_info=True)
        raise RuntimeError(f"items_loader.load_armor: Lua load failed — {e}") from e


def load_materials(lua_engine) -> Optional[dict]:
    """
    Returns a dict of material dicts keyed by material name.
    Raises RuntimeError on failure.
    """
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("items_loader: Lua engine not available — cannot load data")
    try:
        data = lua_engine.load_data("data/items/materials")
        if not data:
            raise RuntimeError(
                "items_loader: materials.lua returned no data — check scripts/data/items/materials.lua"
            )
        raw = data.get("list") or {}
        if not isinstance(raw, dict):
            raise RuntimeError("items_loader: materials.lua 'list' key is not a dict")
        result = {}
        for name, props in raw.items():
            if isinstance(props, dict):
                entry = {str(k): v for k, v in props.items()}
                at = entry.get("apply_to")
                if isinstance(at, dict):
                    entry["apply_to"] = list(at.values())
                elif not isinstance(at, list):
                    entry["apply_to"] = []
                result[str(name)] = entry
        log.info("items_loader: loaded %d materials from Lua", len(result))
        return result
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("items_loader.load_materials: failed: %s", e, exc_info=True)
        raise RuntimeError(f"items_loader.load_materials: Lua load failed — {e}") from e


# ── Normalisation helpers ─────────────────────────────────────────────────────

def _normalise_weapon(raw: dict) -> dict:
    return {
        "base_name":     str(raw.get("base_name", "")),
        "name":          str(raw.get("name", "")),
        "short_name":    str(raw.get("short_name", "")),
        "noun":          str(raw.get("noun", "")),
        "weapon_type":   str(raw.get("weapon_type", "")),
        "damage_factor": float(raw.get("damage_factor", 0.0)),
        "weapon_speed":  int(raw.get("weapon_speed", 5)),
        "damage_type":   str(raw.get("damage_type", "slash")),
        "weight":        float(raw.get("weight", 1.0)),
        "value":         int(raw.get("value", 0)),
        "description":   str(raw.get("description", "")),
    }


def _normalise_armor(raw: dict) -> dict:
    return {
        "base_name":       str(raw.get("base_name", "")),
        "name":            str(raw.get("name", "")),
        "short_name":      str(raw.get("short_name", "")),
        "noun":            str(raw.get("noun", "")),
        "item_type":       str(raw.get("item_type", "armor")),
        "armor_asg":       int(raw.get("armor_asg", 1)),
        "armor_group":     str(raw.get("armor_group", "cloth")),
        "cva":             int(raw.get("cva", 0)),
        "action_penalty":  int(raw.get("action_penalty", 0)),
        "weapon_speed":    int(raw.get("weapon_speed", 0)),
        "spell_hindrance": int(raw.get("spell_hindrance", 0)),
        "weight":          float(raw.get("weight", 1.0)),
        "value":           int(raw.get("value", 0)),
        "description":     str(raw.get("description", "")),
    }
