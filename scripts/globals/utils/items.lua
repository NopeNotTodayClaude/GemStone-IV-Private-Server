---------------------------------------------------
-- globals/utils/items.lua
-- Lua-side item helper wrapping the Python LuaItemsBridge.
-- All Lua scripts do:   local Items = require("globals/utils/items")
-- Then:
--   local item = Items.clone(item_id)      -- clone DB template by items.id
--   local item = Items.create({ name=..., value=..., noun=... })
--
-- Returned item objects support:
--   item:getName()            -> string
--   item:getValue()           -> int
--   item:getBaseItemId()      -> int
--   item:getWeight()          -> float
--   item:getType()            -> string
--   item:getNoun()            -> string
--   item:setName(name)
--   item:setMaterial(mat)
--   item:setColor(color)
--   item:setEnchantBonus(n)
---------------------------------------------------

local Items = {}

local _bridge = _ITEMS_BRIDGE
assert(_bridge, "Items bridge not injected — did LuaEngine._inject_globals() run?")

---------------------------------------------------
-- Items.clone(item_id)
-- Deep-copies a template row from the items table.
---------------------------------------------------
function Items.clone(item_id)
    assert(item_id, "Items.clone: item_id required")
    local ok, result = pcall(function()
        return _bridge:clone(item_id)
    end)
    if not ok then
        print("[Items] clone error: " .. tostring(result))
        return nil
    end
    return result
end

---------------------------------------------------
-- Items.create(props)
-- Build an ad-hoc item from a property table.
-- Example:
--   local coin = Items.create({ name="a silver coin", value=1, noun="coin" })
---------------------------------------------------
function Items.create(props)
    local ok, result = pcall(function()
        return _bridge:create(props)
    end)
    if not ok then
        print("[Items] create error: " .. tostring(result))
        return nil
    end
    return result
end

return Items
