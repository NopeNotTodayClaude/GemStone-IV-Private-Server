# server/core/scripting/loaders/__init__.py
# All Lua data loaders. Each loader tries to read from scripts/data/*.lua
# and returns None on failure so callers fall back to Python hardcoded data.

from .races_loader        import load_races
from .professions_loader  import load_professions
from .skills_loader       import load_skills
from .starter_gear_loader import load_starter_gear
from .items_loader        import load_weapons, load_armor, load_materials
from .shields_loader      import load_shields
from .gems_loader         import load_gems
from .herbs_loader        import load_herbs
from .misc_loader         import load_misc
from .containers_loader   import load_containers
from .lockpicks_loader    import load_lockpicks
from .appearance_loader   import load_appearance
from .ambush_loader       import load_ambush_cfg
from .customize_loader    import load_customize_cfg
from .encumbrance_loader  import load_encumbrance_cfg
from .perception_loader   import load_perception_cfg
from .crafting_loader     import load_crafting
from .perception_loader   import load_perception_cfg

__all__ = [
    "load_races",
    "load_professions",
    "load_skills",
    "load_starter_gear",
    "load_weapons",
    "load_armor",
    "load_materials",
    "load_shields",
    "load_gems",
    "load_herbs",
    "load_misc",
    "load_containers",
    "load_lockpicks",
    "load_appearance",
    "load_ambush_cfg",
    "load_customize_cfg",
    "load_encumbrance_cfg",
    "load_perception_cfg",
    "load_crafting",
    "load_perception_cfg",
]
