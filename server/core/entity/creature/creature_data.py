"""
creature_data.py
----------------
Runtime creature template registry.

ALL creature definitions live in scripts/zones/<zone>/mobs/*.lua
This file contains NO hardcoded creature data.

The registry is populated at server startup by:
    lua_mob_loader.load_all_mob_luas()  ->  register_templates()

If a creature template is missing it means the Lua mob file is missing
or failed to parse.  Fix the Lua file — do not add data here.
"""

import logging
log = logging.getLogger(__name__)

# Populated at startup by lua_mob_loader — do not add hardcoded data here.
CREATURE_TEMPLATES: dict = {}


def get_template(template_id: str) -> dict | None:
    return CREATURE_TEMPLATES.get(template_id)


def get_all_templates() -> dict:
    return dict(CREATURE_TEMPLATES)


def register_templates(new_templates: dict) -> int:
    """
    Merge templates loaded from Lua into the runtime registry.
    Called once at startup by creature_manager.initialize().
    Returns the number of templates registered.
    """
    for tid, tmpl in new_templates.items():
        CREATURE_TEMPLATES[tid] = tmpl
    count = len(new_templates)
    log.info("register_templates: %d templates registered from Lua", count)
    return count
