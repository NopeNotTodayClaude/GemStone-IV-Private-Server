"""
lua_manager.py
--------------
Initialises the LuaEngine at server startup and exposes a single place
to load all Lua data tables.

Usage:
    self.lua = LuaManager(self)
    await self.lua.initialize()
    races_data = self.lua.get_races()

All getters return None ONLY if the Lua engine itself failed to start —
that failure is logged as CRITICAL. Callers that receive None should raise.
There are no Python fallbacks in this codebase. Fix the Lua file.
"""

import logging
import os
from typing import Optional

log = logging.getLogger(__name__)


class LuaManager:
    """Single owner of the LuaEngine; cached data loader results."""

    def __init__(self, server):
        self._server = server
        self._engine = None
        self._cache: dict = {}

    async def initialize(self):
        """Boot the Lua engine.  Safe to call even if lupa is missing."""
        scripts_path = self._server.config.get("paths.scripts", "./scripts")
        scripts_path = os.path.abspath(scripts_path)

        if not os.path.isdir(scripts_path):
            log.warning("LuaManager: scripts_path '%s' not found — Lua disabled", scripts_path)
            return

        try:
            from server.core.scripting.lua_engine import LuaEngine
            self._engine = LuaEngine(
                scripts_path = scripts_path,
                db     = self._server.db,
                world  = self._server.world,
                server = self._server,
            )
            if not self._engine.available:
                log.warning("LuaManager: engine created but lupa unavailable")
                return
            log.info("LuaManager: Lua engine ready (scripts=%s)", scripts_path)
        except Exception as e:
            log.error("LuaManager: engine startup failed: %s", e, exc_info=True)

    @property
    def engine(self):
        """Direct access to the LuaEngine for zone/room/NPC hooks."""
        return self._engine

    # ── Cached data-loader helpers ────────────────────────────────────────────

    def _load_once(self, key: str, loader_fn):
        """
        Run loader_fn and cache the result.
        NEVER caches None — if the loader returns None (Lua not ready yet,
        file parse error, etc.) the next call will retry rather than
        permanently returning None for the lifetime of the server.
        """
        if key not in self._cache or self._cache[key] is None:
            result = loader_fn()
            if result is not None:
                self._cache[key] = result
            return result
        return self._cache[key]

    # ── Character / world data ────────────────────────────────────────────────

    def get_races(self) -> Optional[dict]:
        from server.core.scripting.loaders.races_loader import load_races
        return self._load_once("races", lambda: load_races(self._engine))

    def get_professions(self) -> Optional[dict]:
        from server.core.scripting.loaders.professions_loader import load_professions
        return self._load_once("professions", lambda: load_professions(self._engine))

    def get_skills(self) -> Optional[dict]:
        from server.core.scripting.loaders.skills_loader import load_skills
        return self._load_once("skills", lambda: load_skills(self._engine))

    def get_starter_gear(self) -> Optional[dict]:
        from server.core.scripting.loaders.starter_gear_loader import load_starter_gear
        return self._load_once("starter_gear", lambda: load_starter_gear(self._engine))

    def get_appearance(self) -> Optional[dict]:
        """
        Returns hair/eye/skin options, stat metadata, stat descriptions,
        suggested stat builds, cultures, and age ranges.
        """
        from server.core.scripting.loaders.appearance_loader import load_appearance
        return self._load_once("appearance", lambda: load_appearance(self._engine))

    # ── Item data ─────────────────────────────────────────────────────────────

    def get_weapons(self) -> Optional[dict]:
        from server.core.scripting.loaders.items_loader import load_weapons
        return self._load_once("weapons", lambda: load_weapons(self._engine))

    def get_armor(self) -> Optional[list]:
        from server.core.scripting.loaders.items_loader import load_armor
        return self._load_once("armor", lambda: load_armor(self._engine))

    def get_materials(self) -> Optional[dict]:
        from server.core.scripting.loaders.items_loader import load_materials
        return self._load_once("materials", lambda: load_materials(self._engine))

    def get_shields(self) -> Optional[list]:
        from server.core.scripting.loaders.shields_loader import load_shields
        return self._load_once("shields", lambda: load_shields(self._engine))

    def get_gems(self) -> Optional[list]:
        from server.core.scripting.loaders.gems_loader import load_gems
        return self._load_once("gems", lambda: load_gems(self._engine))

    def get_herbs(self) -> Optional[list]:
        from server.core.scripting.loaders.herbs_loader import load_herbs
        return self._load_once("herbs", lambda: load_herbs(self._engine))

    def get_misc(self) -> Optional[dict]:
        from server.core.scripting.loaders.misc_loader import load_misc
        return self._load_once("misc", lambda: load_misc(self._engine))

    def get_containers(self) -> Optional[dict]:
        from server.core.scripting.loaders.containers_loader import load_containers
        return self._load_once("containers", lambda: load_containers(self._engine))

    def get_lockpicks(self) -> Optional[dict]:
        from server.core.scripting.loaders.lockpicks_loader import load_lockpicks
        return self._load_once("lockpicks", lambda: load_lockpicks(self._engine))


    def get_emotes(self) -> Optional[list]:
        from server.core.scripting.loaders.emotes_loader import load_emotes
        return self._load_once("emotes", lambda: load_emotes(self._engine))

    def get_status_effects(self) -> dict:
        from server.core.scripting.loaders.status_loader import load_status_effects
        return self._load_once("status_effects", lambda: load_status_effects(self._engine))

    def get_ambush_cfg(self) -> dict:
        from server.core.scripting.loaders.ambush_loader import load_ambush_cfg
        return self._load_once("ambush_cfg", lambda: load_ambush_cfg(self._engine))

    def get_customize_cfg(self) -> dict:
        from server.core.scripting.loaders.customize_loader import load_customize_cfg
        return self._load_once("customize_cfg", lambda: load_customize_cfg(self._engine))

    def get_encumbrance_cfg(self) -> dict:
        from server.core.scripting.loaders.encumbrance_loader import load_encumbrance_cfg
        return self._load_once("encumbrance_cfg", lambda: load_encumbrance_cfg(self._engine))

    def get_crafting(self) -> Optional[dict]:
        from server.core.scripting.loaders.crafting_loader import load_crafting
        return self._load_once("crafting", lambda: load_crafting(self._engine))

    def get_adventurers_guild(self) -> Optional[dict]:
        from server.core.scripting.loaders.adventurers_guild_loader import load_adventurers_guild
        return self._load_once("adventurers_guild", lambda: load_adventurers_guild(self._engine))

    def get_skinning(self) -> Optional[dict]:
        from server.core.scripting.loaders.skinning_loader import load_skinning
        return self._load_once("skinning", lambda: load_skinning(self._engine))

    # ── Spell seeding ─────────────────────────────────────────────────────────

    async def seed_spells(self) -> dict:
        """
        Seed the spells table by executing each spell circle's seed() function.
        Safe to call on every startup — circle modules use ON DUPLICATE KEY UPDATE.
        Returns a { circle_name: count } summary dict, or {} if engine is not ready.
        """
        from server.core.scripting.loaders.spells_loader import load_spells
        if not self._engine or not self._engine.available:
            log.warning("LuaManager.seed_spells: Lua engine not ready — spell seeding skipped.")
            return {}
        try:
            summary = load_spells(self._engine) or {}
            total   = sum(summary.values())
            log.info(
                "LuaManager.seed_spells: %d spell(s) seeded across %d circle(s): %s",
                total, len(summary),
                ", ".join(f"{k}={v}" for k, v in sorted(summary.items()))
            )
            return summary
        except Exception as e:
            log.error("LuaManager.seed_spells failed: %s", e, exc_info=True)
            return {}

    # ── Cache management ──────────────────────────────────────────────────────

    def invalidate(self, key: str = None):
        """Clear one or all cached data entries (for live-reload)."""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()
        log.info("LuaManager: cache invalidated (%s)", key or "all")
