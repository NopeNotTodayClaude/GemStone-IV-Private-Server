---------------------------------------------------
-- globals/utils/json.lua
-- Minimal JSON encoder for Lua tables.
-- Used by merchant_base and customize_system to emit
-- hidden HUD tags (SHOP_CATALOG, CUSTOMIZE_MENU, etc.)
--
-- Usage:
--   local JSON = require("globals/utils/json")
--   local str  = JSON.encode({ name = "a broadsword", price = 500 })
--   local str2 = JSON.encodeArray({ {a=1}, {a=2} })
---------------------------------------------------

local JSON = {}

-- ── Internal helpers ─────────────────────────────────────────────────────────

local function _escapeString(s)
    s = s:gsub('\\', '\\\\')
    s = s:gsub('"',  '\\"')
    s = s:gsub('\n', '\\n')
    s = s:gsub('\r', '\\r')
    s = s:gsub('\t', '\\t')
    -- Control chars below 0x20
    s = s:gsub('[\x00-\x1f]', function(c)
        return string.format('\\u%04x', string.byte(c))
    end)
    return s
end

local _encode  -- forward declaration for recursion

local function _isArray(t)
    -- Check if a table is a pure integer-keyed sequential array
    if type(t) ~= "table" then return false end
    local n = #t
    if n == 0 then
        -- Could be empty array or empty object; treat as array
        return next(t) == nil
    end
    for k, _ in pairs(t) do
        if type(k) ~= "number" or k < 1 or k > n or math.floor(k) ~= k then
            return false
        end
    end
    return true
end

_encode = function(val)
    local vtype = type(val)

    if val == nil then
        return "null"
    elseif vtype == "boolean" then
        return val and "true" or "false"
    elseif vtype == "number" then
        -- Use integer format for whole numbers
        if val == math.floor(val) and val >= -2147483648 and val <= 2147483647 then
            return string.format("%d", val)
        end
        return tostring(val)
    elseif vtype == "string" then
        return '"' .. _escapeString(val) .. '"'
    elseif vtype == "table" then
        if _isArray(val) then
            local parts = {}
            for i = 1, #val do
                parts[i] = _encode(val[i])
            end
            return "[" .. table.concat(parts, ",") .. "]"
        else
            local parts = {}
            for k, v in pairs(val) do
                local key = type(k) == "string" and k or tostring(k)
                parts[#parts + 1] = '"' .. _escapeString(key) .. '":' .. _encode(v)
            end
            return "{" .. table.concat(parts, ",") .. "}"
        end
    else
        return "null"
    end
end

---------------------------------------------------
-- JSON.encode(value)
-- Encodes any Lua value (table, string, number, bool, nil) to a JSON string.
---------------------------------------------------
function JSON.encode(value)
    return _encode(value)
end

---------------------------------------------------
-- JSON.encodeArray(array)
-- Explicitly encodes a Lua table as a JSON array.
-- Useful when you know the table is always an array.
---------------------------------------------------
function JSON.encodeArray(arr)
    if type(arr) ~= "table" then return "[]" end
    local parts = {}
    for i = 1, #arr do
        parts[i] = _encode(arr[i])
    end
    return "[" .. table.concat(parts, ",") .. "]"
end

return JSON
