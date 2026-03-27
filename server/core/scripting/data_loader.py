"""
data_loader.py
--------------
Reads Lua data-table files under scripts/data/ and converts them to
native Python structures that the existing Python subsystems can consume.

Usage:
    from server.core.scripting.data_loader import LuaDataLoader

    loader = LuaDataLoader(lua_engine)
    data   = loader.load("data/races")   # returns dict from races.lua
    if data:
        races = data["list"]             # list of race dicts
        mods  = data["stat_mods"]        # race stat mods

Callers MUST fall back to their hardcoded Python tables if load() returns
None (e.g. when lupa is unavailable or a file is missing).
"""

import logging
from typing import Any, Optional

log = logging.getLogger(__name__)


class LuaDataLoader:
    """One-stop loader for all scripts/data/*.lua data tables."""

    def __init__(self, lua_engine):
        self._engine = lua_engine

    def load(self, module_path: str) -> Optional[Any]:
        """
        Load a Lua data module and return Python-native data, or None on failure.
        module_path examples:
          "data/races"
          "data/professions"
          "data/skills"
          "data/items/weapons/edged"
        """
        if not self._engine or not self._engine.available:
            return None
        try:
            data = self._engine.load_data(module_path)
            if data is None:
                log.warning("LuaDataLoader: '%s' returned nil", module_path)
            return data
        except Exception as e:
            log.warning("LuaDataLoader: failed to load '%s': %s", module_path, e)
            return None
