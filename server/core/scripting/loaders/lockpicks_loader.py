"""
lockpicks_loader.py
-------------------
Loads lockpick material and template data from scripts/data/items/lockpicks.lua.

Returns a dict with keys:
  "materials"  - dict keyed by material name with modifier/strength/price data
  "templates"  - list of named lockpick item templates (shop-sold picks)

Returns None on failure.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def load_lockpicks(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("lockpicks_loader: Lua engine not available — cannot load data")
    try:
        data = lua_engine.load_data("data/items/lockpicks")
        if not data:
            raise RuntimeError("lockpicks_loader: Lua returned no data — check scripts/data/ for errors")

        # Materials dict: { material_name: { modifier_mid, mod_min, mod_max, ... } }
        raw_mats = data.get("materials") or {}
        materials = {}
        if isinstance(raw_mats, dict):
            for mat_name, props in raw_mats.items():
                if isinstance(props, dict):
                    materials[str(mat_name)] = {
                        "modifier_mid": float(props.get("modifier_mid", 1.0)),
                        "mod_min":      float(props.get("mod_min", 1.0)),
                        "mod_max":      float(props.get("mod_max", 1.0)),
                        "min_ranks":    int(props.get("min_ranks", 0)),
                        "strength":     int(props.get("strength", 1)),
                        "price":        int(props.get("price", 100)),
                        "precision":    str(props.get("precision", "average")),
                        "desc":         str(props.get("desc", "")),
                    }

        # Templates list: named picks for shop seeding / inventory
        raw_tmpl = data.get("templates") or []
        templates = []
        if isinstance(raw_tmpl, list):
            for t in raw_tmpl:
                if isinstance(t, dict):
                    templates.append({
                        "base_name":  str(t.get("base_name", "")),
                        "name":       str(t.get("name", "")),
                        "noun":       str(t.get("noun", "lockpick")),
                        "item_type":  "lockpick",
                        "material":   str(t.get("material", "steel")),
                        "value":      int(t.get("value", 500)),
                        "weight":     float(t.get("weight", 0.1)),
                        "description":str(t.get("description", "")),
                    })

        log.info("lockpicks_loader: loaded %d materials, %d templates from Lua",
                 len(materials), len(templates))
        return {"materials": materials, "templates": templates}

    except Exception as e:
        log.warning("lockpicks_loader: failed: %s", e)
        raise RuntimeError("lockpicks_loader: unexpected None from Lua loader")
