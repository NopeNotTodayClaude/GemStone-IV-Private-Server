------------------------------------------------------------------------
-- scripts/globals/magic/item_magic.lua
-- Shared helpers for spell-created and spell-modified magic items.
------------------------------------------------------------------------

local DB   = require("globals/utils/db")
local JSON = require("globals/utils/json")

local ItemMagic = {}

local function _decode_extra(extra)
    if not extra or extra == "" then
        return {}
    end
    local ok, parsed = pcall(JSON.decode, extra)
    if ok and type(parsed) == "table" then
        return parsed
    end
    return {}
end

local function _encode_extra(extra)
    return JSON.encode(extra or {})
end

function ItemMagic.get_item_by_inv_id(inv_id)
    if not inv_id then
        return nil
    end
    local row = DB.queryOne([[
        SELECT ci.id AS inv_id, ci.character_id, ci.item_id, ci.slot, ci.quantity, ci.extra_data,
               i.name, i.short_name, i.noun, i.item_type, i.value
        FROM character_inventory ci
        JOIN items i ON i.id = ci.item_id
        WHERE ci.id = ?
        LIMIT 1
    ]], { inv_id })
    if not row then
        return nil
    end
    local extra = _decode_extra(row.extra_data)
    row.extra = extra
    for key, value in pairs(extra) do
        row[key] = value
    end
    return row
end

function ItemMagic.get_held_item(character_id, item_type)
    local sql = [[
        SELECT ci.id AS inv_id, ci.character_id, ci.item_id, ci.slot, ci.quantity, ci.extra_data,
               i.name, i.short_name, i.noun, i.item_type, i.value
        FROM character_inventory ci
        JOIN items i ON i.id = ci.item_id
        WHERE ci.character_id = ?
          AND ci.slot IN ('right_hand', 'left_hand')
    ]]
    local params = { character_id }
    if item_type and item_type ~= "" then
        sql = sql .. " AND i.item_type = ?"
        params[#params + 1] = item_type
    end
    sql = sql .. " ORDER BY FIELD(ci.slot,'right_hand','left_hand'), ci.id LIMIT 1"

    local row = DB.queryOne(sql, params)
    if not row then
        return nil
    end
    local extra = _decode_extra(row.extra_data)
    row.extra = extra
    for key, value in pairs(extra) do
        row[key] = value
    end
    return row
end

function ItemMagic.get_item_by_types(character_id, item_types)
    if type(item_types) ~= "table" or #item_types == 0 then
        return nil
    end
    local placeholders = {}
    local params = { character_id }
    for _, item_type in ipairs(item_types) do
        placeholders[#placeholders + 1] = "?"
        params[#params + 1] = item_type
    end
    local sql = [[
        SELECT ci.id AS inv_id, ci.character_id, ci.item_id, ci.slot, ci.quantity, ci.extra_data,
               i.name, i.short_name, i.noun, i.item_type, i.value
        FROM character_inventory ci
        JOIN items i ON i.id = ci.item_id
        WHERE ci.character_id = ?
          AND i.item_type IN (]] .. table.concat(placeholders, ",") .. [[)
        ORDER BY CASE
            WHEN ci.slot = 'right_hand' THEN 0
            WHEN ci.slot = 'left_hand' THEN 1
            WHEN ci.slot IS NULL THEN 2
            ELSE 3
        END, ci.id
        LIMIT 1
    ]]
    local row = DB.queryOne(sql, params)
    if not row then
        return nil
    end
    local extra = _decode_extra(row.extra_data)
    row.extra = extra
    for key, value in pairs(extra) do
        row[key] = value
    end
    return row
end

function ItemMagic.create_item(character_id, item_id, extra_data, slot)
    DB.execute([[
        INSERT INTO character_inventory (character_id, item_id, slot, quantity, extra_data)
        VALUES (?, ?, ?, 1, ?)
    ]], { character_id, item_id, slot, _encode_extra(extra_data) })
end

function ItemMagic.save_extra(inv_id, extra_data)
    DB.execute("UPDATE character_inventory SET extra_data = ? WHERE id = ?", {
        _encode_extra(extra_data),
        inv_id,
    })
end

function ItemMagic.remove_item(inv_id)
    DB.execute("DELETE FROM character_inventory WHERE id = ?", { inv_id })
end

function ItemMagic.bump_charges(inv_id, delta, max_charges)
    local item = ItemMagic.get_item_by_inv_id(inv_id)
    if not item then
        return nil, "That item cannot be found."
    end
    local extra = item.extra or {}
    local charges = math.max(0, tonumber(extra.charges) or tonumber(item.charges) or 0)
    if max_charges then
        charges = math.min(max_charges, charges + delta)
    else
        charges = math.max(0, charges + delta)
    end
    extra.charges = charges
    ItemMagic.save_extra(inv_id, extra)
    return charges, item
end

return ItemMagic
