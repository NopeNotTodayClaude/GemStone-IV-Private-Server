---------------------------------------------------
-- globals/utils/db.lua
-- Clean Lua-side DB wrapper over the Python LuaDBBridge.
-- All Lua scripts do:   local DB = require("globals/utils/db")
-- Then:
--   local rows = DB.query("SELECT ...", { param1, param2 })
--   local row  = DB.queryOne("SELECT ... LIMIT 1", { id })
--   DB.execute("UPDATE ...", { val1, val2 })
---------------------------------------------------

local DB = {}

-- _DB_BRIDGE is injected by lua_engine.py at startup
local _bridge = _DB_BRIDGE
assert(_bridge, "DB bridge not injected — did LuaEngine._inject_globals() run?")

---------------------------------------------------
-- DB.query(sql, params)
-- Returns an array of row-tables, or {} on error.
---------------------------------------------------
function DB.query(sql, params)
    local ok, result = pcall(function()
        return _bridge:query(sql, params)
    end)
    if not ok then
        print("[DB] query error: " .. tostring(result))
        return {}
    end
    return result or {}
end

---------------------------------------------------
-- DB.queryOne(sql, params)
-- Returns the first row-table, or nil if no rows.
---------------------------------------------------
function DB.queryOne(sql, params)
    local ok, result = pcall(function()
        return _bridge:queryOne(sql, params)
    end)
    if not ok then
        print("[DB] queryOne error: " .. tostring(result))
        return nil
    end
    return result
end

---------------------------------------------------
-- DB.execute(sql, params)
-- Runs INSERT / UPDATE / DELETE.  No return value.
---------------------------------------------------
function DB.execute(sql, params)
    local ok, err = pcall(function()
        _bridge:execute(sql, params)
    end)
    if not ok then
        print("[DB] execute error: " .. tostring(err))
    end
end

return DB
