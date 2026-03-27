---------------------------------------------------
-- merchant_base.lua
-- Shared logic for all standard shopkeeper NPCs.
-- Usage:  local Merchant = require("npcs/merchants/merchant_base")
--         local npc = Merchant.new({ shop_id=16, npc_name="Raeliveth", ... })
--
-- Commands handled:
--   ORDER / LIST           - show shop inventory table
--   BUY #  / BUY <name>   - purchase item by number or partial name
--   SELL <item>            - sell held item to shopkeeper
--   (entry)                - NPC greets player on room enter
---------------------------------------------------

local DB    = require("globals/utils/db")      -- your DB query wrapper
local Items = require("globals/utils/items")   -- item spawn/clone helpers

local Merchant = {}
Merchant.__index = Merchant

-- ── Column widths for ORDER listing ──────────────────────────────────────────
local COL_NUM   = 4
local COL_ITEM  = 35
local COL_PRICE = 12
local DIVIDER   = string.rep("=", COL_NUM + COL_ITEM + COL_PRICE + 4)
local SUB_DIV   = string.rep("-", COL_NUM + COL_ITEM + COL_PRICE + 4)

-- ── Material tier data (used by custom shops; ignored by clothiers) ──────────
-- Populated externally by customize_system if needed.
Merchant.MATERIALS = nil

-- ─────────────────────────────────────────────────────────────────────────────
-- Constructor
-- opts = {
--   shop_id      (int)     required – matches shops.id in DB
--   npc_name     (string)  required – display name e.g. "Raeliveth"
--   entry_lines  (table)   optional – list of strings NPC says/emotes on entry
--   allow_sell   (bool)    default true
--   allow_buy    (bool)    default true
-- }
-- ─────────────────────────────────────────────────────────────────────────────
function Merchant.new(opts)
    assert(opts.shop_id,  "merchant_base: shop_id required")
    assert(opts.npc_name, "merchant_base: npc_name required")

    local self = setmetatable({}, Merchant)
    self.shop_id     = opts.shop_id
    self.npc_name    = opts.npc_name
    self.allow_sell  = (opts.allow_sell ~= false)
    self.allow_buy   = (opts.allow_buy  ~= false)

    -- Default greeting lines; override per NPC.
    self.entry_lines = opts.entry_lines or {
        self.npc_name .. " looks up and gives you a welcoming nod.",
    }

    return self
end

-- ─────────────────────────────────────────────────────────────────────────────
-- Internal: load shop inventory from DB
-- Returns ordered list of { num, item_id, name, price, stock, level_req }
-- ─────────────────────────────────────────────────────────────────────────────
function Merchant:_loadInventory()
    local rows = DB.query([[
        SELECT
            ROW_NUMBER() OVER (ORDER BY i.item_type, i.name) AS num,
            si.item_id,
            i.name,
            ROUND(i.value * s.buy_multiplier) AS price,
            si.stock,
            i.level_required
        FROM shop_inventory si
        JOIN items  i ON i.id  = si.item_id
        JOIN shops  s ON s.id  = si.shop_id
        WHERE si.shop_id = ?
          AND (si.stock > 0 OR si.stock = -1)
        ORDER BY i.item_type, i.name
    ]], { self.shop_id })
    return rows or {}
end

-- ─────────────────────────────────────────────────────────────────────────────
-- Internal: find inventory row by number or partial name
-- ─────────────────────────────────────────────────────────────────────────────
function Merchant:_findItem(inv, query)
    -- Try numeric index first
    local n = tonumber(query)
    if n then
        for _, row in ipairs(inv) do
            if row.num == n then return row end
        end
        return nil
    end
    -- Partial name match (case-insensitive)
    local q = query:lower()
    for _, row in ipairs(inv) do
        if row.name:lower():find(q, 1, true) then return row end
    end
    return nil
end

-- ─────────────────────────────────────────────────────────────────────────────
-- onEnter(player)  – fired when a player enters the NPC's room
-- ─────────────────────────────────────────────────────────────────────────────
function Merchant:onEnter(player)
    for _, line in ipairs(self.entry_lines) do
        player:roomMessage(line)
    end
    player:message("Type ORDER to see available items, BUY # or BUY <name> to purchase, SELL <item> to sell.")
end

-- ─────────────────────────────────────────────────────────────────────────────
-- onCommand(player, cmd, args)
-- cmd is the first word uppercased; args is everything after.
-- Return true if the command was handled, false to pass through.
-- ─────────────────────────────────────────────────────────────────────────────
function Merchant:onCommand(player, cmd, args)
    if cmd == "ORDER" or cmd == "LIST" then
        return self:_cmdOrder(player, args)
    elseif cmd == "BUY" and self.allow_buy then
        return self:_cmdBuy(player, args)
    elseif cmd == "SELL" and self.allow_sell then
        return self:_cmdSell(player, args)
    end
    return false
end

-- ── ORDER / LIST ──────────────────────────────────────────────────────────────
function Merchant:_cmdOrder(player, args)
    local inv = self:_loadInventory()

    if #inv == 0 then
        player:message(self.npc_name .. " shakes their head. \"I'm afraid I have nothing for sale right now.\"")
        return true
    end

    -- Header
    local shopName = DB.queryOne("SELECT name FROM shops WHERE id=?", { self.shop_id })
    player:message("")
    player:message((shopName and shopName.name) or "Shop Inventory")
    player:message(DIVIDER)
    player:message(string.format("%-"..COL_NUM.."s  %-"..COL_ITEM.."s  %s", "#", "Item", "Price"))
    player:message(SUB_DIV)

    for _, row in ipairs(inv) do
        -- Grey out (mark with *) items the player doesn't meet level for
        local suffix = ""
        if row.level_required and player:getLevel() < row.level_required then
            suffix = " *"
        end
        local priceStr
        if row.stock == -1 then
            priceStr = string.format("%d silver", row.price)
        else
            priceStr = string.format("%d silver (%d left)", row.price, row.stock)
        end
        player:message(string.format("%-"..COL_NUM.."s  %-"..COL_ITEM.."s  %s%s",
            tostring(row.num), row.name, priceStr, suffix))
    end

    player:message(DIVIDER)
    player:message("* Item requires a higher level than you currently have.")
    player:message("Type BUY # or BUY <item name> to purchase.")
    return true
end

-- ── BUY ───────────────────────────────────────────────────────────────────────
function Merchant:_cmdBuy(player, args)
    if not args or args == "" then
        player:message("Buy what?  Use ORDER to see available items, then BUY # or BUY <name>.")
        return true
    end

    local inv  = self:_loadInventory()
    local row  = self:_findItem(inv, args:match("^%s*(.-)%s*$"))

    if not row then
        player:message(self.npc_name .. " shakes their head. \"I don't have that.\"")
        return true
    end

    -- Level check
    if row.level_required and player:getLevel() < row.level_required then
        player:message(self.npc_name .. " says, \"You don't yet have the experience to use that.\"")
        return true
    end

    local price = row.price

    -- Silver check
    if player:getSilver() < price then
        player:message(self.npc_name .. " says, \"That'll be "..price.." silvers, and you're a bit short.\"")
        return true
    end

    -- Deduct silver, clone item, add to player inventory
    player:deductSilver(price)
    local newItem = Items.clone(row.item_id)
    player:giveItem(newItem)

    -- Decrement stock if not unlimited
    if row.stock ~= -1 then
        DB.execute([[
            UPDATE shop_inventory SET stock = stock - 1
            WHERE shop_id=? AND item_id=? AND stock > 0
        ]], { self.shop_id, row.item_id })
    end

    -- Log transaction
    DB.execute([[
        INSERT INTO transaction_log (character_id, transaction_type, item_id, silver_amount, notes)
        VALUES (?, 'buy', ?, ?, ?)
    ]], { player:getId(), row.item_id, price, "shop_id="..self.shop_id })

    player:message(self.npc_name .. " hands you " .. row.name .. ".")
    player:roomMessage(player:getName() .. " purchases " .. row.name .. " from " .. self.npc_name .. ".", player)
    return true
end

-- ── SELL ──────────────────────────────────────────────────────────────────────
function Merchant:_cmdSell(player, args)
    if not args or args == "" then
        player:message("Sell what?  Hold the item and type SELL <item name>.")
        return true
    end

    local item = player:findHeldItem(args)
    if not item then
        player:message("You don't seem to be holding that.")
        return true
    end

    -- Fetch sell multiplier for this shop
    local shop    = DB.queryOne("SELECT sell_multiplier FROM shops WHERE id=?", { self.shop_id })
    local mult    = (shop and shop.sell_multiplier) or 0.40
    local baseVal = item:getValue()   -- uses item.value from items table
    local offer   = math.max(1, math.floor(baseVal * mult))

    player:removeheldItem(item)
    player:addSilver(offer)

    DB.execute([[
        INSERT INTO transaction_log (character_id, transaction_type, item_id, silver_amount, notes)
        VALUES (?, 'sell', ?, ?, ?)
    ]], { player:getId(), item:getBaseItemId(), offer, "shop_id="..self.shop_id })

    player:message(self.npc_name .. " examines " .. item:getName() .. " and hands you " .. offer .. " silvers.")
    player:roomMessage(player:getName() .. " sells " .. item:getName() .. " to " .. self.npc_name .. ".", player)
    return true
end

return Merchant
