"""
server/core/engine/material_weight.py
--------------------------------------
Standalone material weight modifier cache.

Lives OUTSIDE the combat package deliberately so that encumbrance.py can
import from here without triggering the combat/__init__.py -> combat_engine
-> encumbrance circular import chain.

Call init_weight_cache(server) once at startup (game_server.py does this).
effective_weight(item) is then safe to call from anywhere with zero I/O.
"""

import logging

log = logging.getLogger(__name__)

# material_name (lowercase str) -> weight_modifier (float)
_WEIGHT_MODIFIERS: dict = {}


def init_weight_cache(server) -> None:
    """
    Populate the weight modifier cache from the Lua materials table.
    Called once from game_server.py right after lua.initialize().
    """
    global _WEIGHT_MODIFIERS
    try:
        materials = server.lua.get_materials()
        if materials:
            for name, data in materials.items():
                mod = data.get("weight_modifier", 1.0)
                _WEIGHT_MODIFIERS[str(name).lower()] = float(mod)
            log.info(
                "material_weight: cache loaded (%d materials)", len(_WEIGHT_MODIFIERS)
            )
        else:
            log.warning("material_weight: Lua materials unavailable, all modifiers default 1.0")
    except Exception as e:
        log.error("material_weight.init_weight_cache: %s", e)


def effective_weight(item: dict) -> float:
    """
    Returns the effective weight of an item after applying its material's
    weight_modifier.  Safe to call before init_weight_cache() — defaults to 1.0.

    Args:
        item: item dict with at minimum {'weight': N, 'material': '...'}

    Returns:
        float: effective weight in pounds
    """
    if not item:
        return 0.0
    base = float(item.get("weight") or 0)
    if base <= 0:
        return 0.0
    material = (item.get("material") or "").lower()
    modifier = _WEIGHT_MODIFIERS.get(material, 1.0)
    return base * modifier
