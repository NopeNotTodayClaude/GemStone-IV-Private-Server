"""
db_bridge.py
------------
Exposes the Python Database object to Lua scripts.

Injected into Lua globals as _DB_BRIDGE.
Consumed by scripts/globals/utils/db.lua which provides the clean Lua API.

Methods (callable from Lua via the db.lua wrapper):
  query(sql, params)     -> Lua array of row-tables
  queryOne(sql, params)  -> single Lua row-table or nil
  execute(sql, params)   -> nil  (INSERT/UPDATE/DELETE)

NOTE: Lua scripts use '?' as parameter placeholders (SQLite/JDBC style).
      mysql.connector requires '%s'.  _sanitize_sql() handles translation.
"""

import logging
import re
from typing import Any, Optional

log = logging.getLogger(__name__)


class LuaDBBridge:
    """Python-side DB bridge.  One instance shared by all Lua scripts."""

    def __init__(self, db, lua_runtime):
        self._db  = db
        self._lua = lua_runtime

    # ── Internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _sanitize_sql(sql: str, has_params: bool = False) -> str:
        """
        Translate Lua-style '?' placeholders to MySQL-style '%s'.
        Preserve existing '%s' placeholders for newer callers while escaping
        other literal '%' tokens that mysql.connector would treat as Python
        formatting markers during bound execution.
        """
        if has_params:
            sql = re.sub(r"%(?!s)", "%%", sql)
        sql = sql.replace('?', '%s')
        return sql

    def _to_lua_table(self, data):
        """Convert Python dict/list to a Lua table recursively."""
        if isinstance(data, dict):
            tbl = self._lua.eval("{}")
            for k, v in data.items():
                tbl[k] = self._to_lua_table(v)
            return tbl
        if isinstance(data, (list, tuple)):
            tbl = self._lua.eval("{}")
            for i, v in enumerate(data, 1):
                tbl[i] = self._to_lua_table(v)
            return tbl
        return data

    def _normalize_params(self, params):
        """Convert a Lua table of params to a Python tuple."""
        if params is None:
            return None
        try:
            import lupa
            if lupa.lua_type(params) == "table":
                items = list(params.items())
                if not items:
                    return tuple()
                numeric = []
                other = []
                for key, value in items:
                    if isinstance(key, (int, float)) and int(key) == key:
                        numeric.append((int(key), value))
                    else:
                        other.append((key, value))
                if numeric and not other:
                    numeric.sort(key=lambda kv: kv[0])
                    return tuple(value for _, value in numeric)
                items.sort(key=lambda kv: str(kv[0]))
                return tuple(value for _, value in items)
        except Exception:
            pass
        if isinstance(params, (list, tuple)):
            return tuple(params)
        return None

    def _raw_query(self, sql: str, params=None):
        """Execute SQL using a raw dictionary cursor."""
        sql = self._sanitize_sql(sql, has_params=bool(params))
        conn = self._db._get_conn()
        try:
            import mysql.connector
            cur = conn.cursor(dictionary=True)
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            rows = cur.fetchall()
            return rows
        except Exception as e:
            log.error(
                "LuaDBBridge.query error: %s | params=%s | SQL: %s",
                e,
                len(params) if params is not None else 0,
                sql[:200],
            )
            return []
        finally:
            conn.close()

    def _raw_execute(self, sql: str, params=None):
        """Execute a non-SELECT statement."""
        sql = self._sanitize_sql(sql, has_params=bool(params))
        conn = self._db._get_conn()
        try:
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
        except Exception as e:
            log.error(
                "LuaDBBridge.execute error: %s | params=%s | SQL: %s",
                e,
                len(params) if params is not None else 0,
                sql[:200],
            )
        finally:
            conn.close()

    # ── Lua-callable API ──────────────────────────────────────────────────────

    def query(self, sql: str, params=None):
        """
        Execute SELECT and return all rows as a Lua array of tables.
        Usage in Lua:  local rows = DB.query("SELECT ...", {param1, param2})
        """
        p = self._normalize_params(params)
        rows = self._raw_query(sql, p)
        return self._to_lua_table(rows)

    def queryOne(self, sql: str, params=None):
        """
        Execute SELECT and return the first row as a Lua table, or nil.
        Usage in Lua:  local row = DB.queryOne("SELECT ... LIMIT 1", {id})
        """
        p = self._normalize_params(params)
        rows = self._raw_query(sql, p)
        if not rows:
            return None
        return self._to_lua_table(rows[0])

    def execute(self, sql: str, params=None):
        """
        Execute a non-SELECT statement (INSERT/UPDATE/DELETE).
        Usage in Lua:  DB.execute("UPDATE ...", {val1, val2})
        """
        p = self._normalize_params(params)
        self._raw_execute(sql, p)
