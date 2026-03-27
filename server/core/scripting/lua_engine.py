"""
lua_engine.py
-------------
Central Lua runtime for GemStone IV.

All Lua scripts (zones, rooms, NPCs, data files) run through this engine.
Uses lupa (LuaRuntime wrapping Lua 5.4) for full two-way Python<->Lua bridging.

require() resolution order:
  1. scripts/<module>.lua
  2. scripts/<module>/init.lua

Python objects injected into Lua globals:
  _DB_BRIDGE    -> LuaDBBridge    (used by globals/utils/db.lua)
  _ITEMS_BRIDGE -> LuaItemsBridge (used by globals/utils/items.lua)

Hook calling convention:
  lua_engine.call_hook(lua_table, "onEnter", player_api)
  -> silently no-ops if the function does not exist
"""

import os
import logging
import asyncio
from typing import Any, Optional

log = logging.getLogger(__name__)

try:
    import lupa
    from lupa import LuaRuntime
    LUPA_AVAILABLE = True
except ImportError:
    LUPA_AVAILABLE = False
    log.warning("lupa not installed — Lua scripting disabled.  Run: pip install lupa")


def lua_to_python(val, _depth=0):
    """
    Recursively convert a Lua value to native Python.
    Lua arrays  (1-indexed int keys) -> list
    Lua hashes  (string keys)        -> dict
    Mixed                            -> dict (int keys preserved)
    Primitives                       -> unchanged

    Defensive against lupa version differences: if lua_type() doesn't identify
    the value as a table but it has an items() method (i.e. it IS a lupa table
    object that the version wraps differently), we process it as a table anyway.
    """
    if not LUPA_AVAILABLE:
        return val
    if _depth > 64:
        return {}

    is_table = lupa.lua_type(val) == "table"

    # Fallback for lupa/Python version differences where lua_type() may not
    # return "table" for a valid Lua table object (e.g. lupa 2.6 + Python 3.14).
    if not is_table and hasattr(val, "items") and callable(val.items):
        try:
            # Confirm it's actually iterable as key/value pairs
            _ = list(val.items())
            is_table = True
        except Exception:
            pass

    if is_table:
        pairs = list(val.items())
        # Pure integer-keyed sequential table -> list
        int_keys = [k for k, _ in pairs if isinstance(k, int)]
        str_keys = [k for k, _ in pairs if not isinstance(k, int)]
        if int_keys and not str_keys:
            max_k = max(int_keys)
            result = [None] * max_k
            for k, v in pairs:
                result[k - 1] = lua_to_python(v, _depth + 1)
            return result
        # Otherwise -> dict
        result = {}
        for k, v in pairs:
            result[k] = lua_to_python(v, _depth + 1)
        return result
    return val




def _unwrap_lua_result(val):
    """
    Lua require() and eval() may return multiple values.
    With unpack_returned_tuples=False, lupa wraps multi-return into a Python
    tuple.  We only want the first value (the module table), not the trailing
    loader path string that require() appends.

    Also handles the edge case where load_file()/execute() return tuples.
    """
    if isinstance(val, tuple):
        return val[0] if val else None
    return val


def python_to_lua(val, lua_runtime, _depth=0):
    """Convert a Python dict/list into a Lua table."""
    if not LUPA_AVAILABLE:
        return val
    if _depth > 64:
        return lua_runtime.eval("{}")
    if isinstance(val, dict):
        tbl = lua_runtime.eval("{}")
        for k, v in val.items():
            tbl[k] = python_to_lua(v, lua_runtime, _depth + 1)
        return tbl
    if isinstance(val, (list, tuple)):
        tbl = lua_runtime.eval("{}")
        for i, v in enumerate(val, 1):
            tbl[i] = python_to_lua(v, lua_runtime, _depth + 1)
        return tbl
    return val


class LuaEngine:
    """
    Manages the shared Lua runtime.  One instance per server process.
    Thread-safety note: lupa's LuaRuntime is NOT thread-safe by default.
    All calls must come from the same event-loop thread (the asyncio loop).
    """

    def __init__(self, scripts_path: str, db=None, world=None, server=None):
        self._scripts_path = os.path.abspath(scripts_path)
        self._db     = db
        self._world  = world
        self._server = server
        self._lua: Optional["LuaRuntime"] = None
        self._loaded: dict = {}   # cache: module path -> Lua table result

        if not LUPA_AVAILABLE:
            log.warning("LuaEngine: lupa unavailable, engine disabled")
            return

        # unpack_returned_tuples=False is required for Python 3.14 + lupa 2.6 compatibility.
        # With True, require() returns land as raw Python tuples instead of _LuaTable objects,
        # causing lua_to_python() to fall through and return them unconverted.
        self._lua = LuaRuntime(unpack_returned_tuples=False)
        self._setup_package_path()
        self._inject_globals()
        log.info("LuaEngine initialised (scripts_path=%s)", self._scripts_path)

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _setup_package_path(self):
        sp = self._scripts_path.replace("\\", "/")
        self._lua.execute(f'''
            package.path = "{sp}/?.lua;{sp}/?/init.lua;" .. package.path
        ''')

    def _inject_globals(self):
        from server.core.scripting.lua_bindings.db_bridge import LuaDBBridge
        from server.core.scripting.lua_bindings.items_api import LuaItemsBridge

        g = self._lua.globals()

        if self._db:
            g._DB_BRIDGE    = LuaDBBridge(self._db, self._lua)
        if self._server:
            g._ITEMS_BRIDGE = LuaItemsBridge(self._server, self._lua)

        # scheduleCallback(seconds, fn) — Lua timer helper
        g.scheduleCallback = self._make_schedule_callback()

        # print() override so Lua output goes to Python logging
        self._lua.execute("""
            local _orig_print = print
            print = function(...)
                local t = {}
                for i = 1, select('#', ...) do
                    t[i] = tostring(select(i, ...))
                end
                _orig_print(table.concat(t, "\\t"))
            end
        """)

    def _make_schedule_callback(self):
        def schedule_callback(seconds, fn):
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                pass
            if loop and loop.is_running():
                async def _runner():
                    await asyncio.sleep(seconds)
                    try:
                        fn()
                    except Exception as e:
                        log.error("scheduleCallback error: %s", e)
                asyncio.ensure_future(_runner(), loop=loop)
            else:
                log.warning("scheduleCallback called outside event loop — skipped")
        return schedule_callback

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def available(self) -> bool:
        return self._lua is not None

    def load_file(self, filepath: str) -> Any:
        """
        Execute a Lua file and return its return value (usually a table).
        Raises on syntax/runtime error.
        """
        if not self._lua:
            return None
        filepath = os.path.abspath(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            src = f.read()
        result = self._lua.execute(src)
        return _unwrap_lua_result(result)

    def require(self, module_path: str) -> Any:
        """
        Load a scripts/<module_path>.lua via Lua's require().
        Result is cached by Lua's own package.loaded mechanism.
        """
        if not self._lua:
            return None
        result = self._lua.eval(f'require("{module_path}")')
        # require() returns (module, path) — unwrap to just the module table
        return _unwrap_lua_result(result)

    def load_data(self, module_path: str) -> Any:
        """
        Load a data module (e.g. 'data/races') and return Python-native data.
        The Lua file must return a table.
        Raises on error so callers can fall back gracefully.
        """
        if not self._lua:
            raise RuntimeError("Lua engine not available")
        lua_result = self._lua.eval(f'require("{module_path}")')
        # require() may return (module, path) tuple — unwrap first
        lua_result = _unwrap_lua_result(lua_result)
        return lua_to_python(lua_result)

    def call_hook(self, lua_table: Any, hook: str, *args) -> Any:
        """
        Call lua_table.<hook>(*args) if the function exists.
        Returns the hook's return value, or None if not defined.
        """
        if not self._lua or lua_table is None:
            return None
        try:
            fn = getattr(lua_table, hook, None)
            if fn is None or lupa.lua_type(fn) != "function":
                return None
            return fn(*args)
        except Exception as e:
            log.error("Lua hook '%s' error: %s", hook, e)
            return None

    def execute(self, code: str) -> Any:
        """Execute arbitrary Lua code.  For testing / GM commands."""
        if not self._lua:
            return None
        return self._lua.execute(code)

    def python_to_lua(self, val: Any) -> Any:
        """Convert a Python value to a Lua-compatible table."""
        if not self._lua:
            return val
        return python_to_lua(val, self._lua)

    def lua_to_python(self, val: Any) -> Any:
        """Convert a Lua value to native Python."""
        return lua_to_python(val)
