---------------------------------------------------
-- customize_system.lua
-- Centralized weapon/armor customization module.
--
-- GS4-accurate flow (accelerated wait times):
--   ORDER                         – browse base items + prices
--   CUSTOMIZE <item#>             – show material options for that item
--   CUSTOMIZE <item#> <mat#>      – select item + material, show color prompt
--   CUSTOMIZE <item#> <mat#> <color> – full one-shot: item + material + color
--   CONFIRM                       – place order, start 1-3 min timer
--   (timer fires)                 – NPC calls player's name, hands item
--
-- Grey entries (level_required > player level) show in list but block purchase.
-- BUY alone after CUSTOMIZE still works (backward-compat with image 3 confusion).
---------------------------------------------------

local DB    = require("globals/utils/db")
local Items = require("globals/utils/items")

local Customize = {}
Customize.__index = Customize

-- ── Material table ────────────────────────────────────────────────────────────
-- Ordered for display; tier drives price multiplier and craft time.
-- enchant = enchantment bonus on finished item
-- mult    = price multiplier applied on top of the shop's buy_multiplier
-- time_s  = craft time in seconds (1–3 min range)
-- level   = minimum character level to order
Customize.MATERIALS = {
    { id=1,  name="iron",    enchant=0,  mult=0.80, time_s=60,  level=0  },
    { id=2,  name="bronze",  enchant=0,  mult=0.90, time_s=60,  level=0  },
    { id=3,  name="steel",   enchant=0,  mult=1.00, time_s=70,  level=0  },
    { id=4,  name="ora",     enchant=15, mult=2.50, time_s=90,  level=10 },
    { id=5,  name="invar",   enchant=15, mult=2.50, time_s=90,  level=10 },
    { id=6,  name="mithril", enchant=10, mult=2.00, time_s=90,  level=10 },
    { id=7,  name="vultite", enchant=20, mult=3.50, time_s=110, level=20 },
    { id=8,  name="kelyn",   enchant=20, mult=3.50, time_s=110, level=20 },
    { id=9,  name="laje",    enchant=20, mult=3.50, time_s=110, level=20 },
    { id=10, name="rolaren", enchant=25, mult=5.00, time_s=130, level=30 },
    { id=11, name="faenor",  enchant=25, mult=5.00, time_s=130, level=30 },
    { id=12, name="eahnor",  enchant=25, mult=5.00, time_s=130, level=30 },
    { id=13, name="imflass", enchant=30, mult=7.00, time_s=150, level=40 },
    { id=14, name="vaalorn", enchant=30, mult=7.00, time_s=150, level=40 },
    { id=15, name="golvern", enchant=35, mult=9.00, time_s=180, level=50 },
}

-- ── Divider widths ────────────────────────────────────────────────────────────
local DIVIDER  = string.rep("=", 60)
local SUB_DIV  = string.rep("-", 60)

-- ─────────────────────────────────────────────────────────────────────────────
-- Constructor
-- opts = {
--   shop_id   (int)    required
--   npc_name  (string) required
-- }
-- ─────────────────────────────────────────────────────────────────────────────
function Customize.new(opts)
    assert(opts.shop_id,  "customize_system: shop_id required")
    assert(opts.npc_name, "customize_system: npc_name required")
    local self = setmetatable({}, Customize)
    self.shop_id  = opts.shop_id
    self.npc_name = opts.npc_name
    -- Per-player pending order state keyed by player:getId()
    -- state[pid] = { item_row, mat, color, price, confirmed=false }
    self._state   = {}
    return self
end

-- ─────────────────────────────────────────────────────────────────────────────
-- Internal helpers
-- ─────────────────────────────────────────────────────────────────────────────
function Customize:_getInventory()
    local rows = DB.query([[
        SELECT
            ROW_NUMBER() OVER (ORDER BY i.name) AS num,
            si.item_id,
            i.name,
            ROUND(i.value * s.buy_multiplier) AS base_price,
            i.level_required
        FROM shop_inventory si
        JOIN items i ON i.id  = si.item_id
        JOIN shops s ON s.id  = si.shop_id
        WHERE si.shop_id = ?
          AND (si.stock > 0 OR si.stock = -1)
        ORDER BY i.name
    ]], { self.shop_id })
    return rows or {}
end

function Customize:_getMat(mat_id)
    local n = tonumber(mat_id)
    if n then
        for _, m in ipairs(Customize.MATERIALS) do
            if m.id == n then return m end
        end
    end
    -- Also allow material name lookup
    local q = tostring(mat_id):lower()
    for _, m in ipairs(Customize.MATERIALS) do
        if m.name == q then return m end
    end
    return nil
end

function Customize:_calcPrice(base_price, mat)
    return math.max(1, math.floor(base_price * mat.mult))
end

-- ─────────────────────────────────────────────────────────────────────────────
-- onCommand(player, cmd, args)  – plug into NPC command dispatcher
-- ─────────────────────────────────────────────────────────────────────────────
function Customize:onCommand(player, cmd, args)
    if cmd == "CUSTOMIZE" then
        return self:_cmdCustomize(player, args)
    elseif cmd == "CONFIRM" then
        return self:_cmdConfirm(player)
    elseif cmd == "BUY" and (not args or args == "") then
        -- Bare BUY with an active pending order = alias for CONFIRM
        local st = self._state[player:getId()]
        if st and not st.confirmed then
            return self:_cmdConfirm(player)
        end
    end
    return false
end

-- ─────────────────────────────────────────────────────────────────────────────
-- CUSTOMIZE [item#] [mat#] [color]
-- ─────────────────────────────────────────────────────────────────────────────
function Customize:_cmdCustomize(player, args)
    local inv = self:_getInventory()

    -- No args → show item list with instruction
    if not args or args == "" then
        self:_showItemList(player, inv)
        return true
    end

    -- Parse args: could be "5", "5 3", "5 3 silver", "22 5 Silver"
    local parts = {}
    for w in args:gmatch("%S+") do parts[#parts+1] = w end

    local item_arg = parts[1]
    local mat_arg  = parts[2]
    local color    = parts[3]  -- optional

    -- Find item
    local item_row = nil
    local n = tonumber(item_arg)
    if n then
        for _, r in ipairs(inv) do
            if r.num == n then item_row = r; break end
        end
    end
    if not item_row then
        -- Try partial name
        local q = item_arg:lower()
        for _, r in ipairs(inv) do
            if r.name:lower():find(q, 1, true) then item_row = r; break end
        end
    end
    if not item_row then
        player:message(self.npc_name .. " shakes their head. \"I don't carry that.\"")
        return true
    end

    -- Level check
    local req = item_row.level_required or 0
    if player:getLevel() < req then
        player:message(self.npc_name .. " says, \"You don't have the experience to wield that yet.\"")
        return true
    end

    -- No material specified → show material list for this item
    if not mat_arg then
        self:_showMaterialList(player, item_row)
        return true
    end

    -- Find material
    local mat = self:_getMat(mat_arg)
    if not mat then
        player:message("That's not a valid material.  Type CUSTOMIZE "..item_row.num.." to see available materials.")
        return true
    end

    -- Material level check
    if player:getLevel() < mat.level then
        player:message(self.npc_name .. " says, \"You lack the experience to handle "..mat.name.." equipment.\"")
        return true
    end

    -- Price
    local price = self:_calcPrice(item_row.base_price, mat)

    -- Silver check
    if player:getSilver() < price then
        player:message(self.npc_name .. " says, \"That'll be "..price.." silvers for "..mat.name.." work, and you're a bit short.\"")
        return true
    end

    -- Validate color if provided (basic alpha check, no DB needed)
    local colorStr = nil
    if color and color ~= "" then
        if not color:match("^%a+$") then
            player:message("That doesn't look like a valid color name.  Use a single word, like 'silver' or 'crimson'.")
            return true
        end
        colorStr = color:lower()
    end

    -- Save pending state
    self._state[player:getId()] = {
        item_row  = item_row,
        mat       = mat,
        color     = colorStr,
        price     = price,
        confirmed = false,
    }

    -- Show selection summary and prompt for CONFIRM
    local colorDesc = colorStr and (" "..colorStr.."-colored") or ""
    local enchDesc  = mat.enchant > 0 and (" (+"..(mat.enchant).." enchantment)") or ""
    player:message("")
    player:message("You select a"..colorDesc.." "..mat.name.." "..item_row.name:match("^%a+%s+(.-)%s*$")..enchDesc..".")
    player:message(string.format("Total price: %d silvers.", price))
    player:message("")
    player:message(self.npc_name.." says, \"Shall I craft that for you?  Type CONFIRM to place your order, or CUSTOMIZE again to change your selection.\"")
    return true
end

-- ── Show item list ─────────────────────────────────────────────────────────────
function Customize:_showItemList(player, inv)
    if #inv == 0 then
        player:message(self.npc_name.." says, \"I have nothing available to customize right now.\"")
        return
    end
    player:message("")
    player:message(self.npc_name.."'s Customization Menu")
    player:message(DIVIDER)
    player:message(string.format("%-4s  %-34s  %s", "#", "Item", "Base Price"))
    player:message(SUB_DIV)
    for _, r in ipairs(inv) do
        local lev = (r.level_required and r.level_required > 0) and (" (lvl "..r.level_required..")") or ""
        player:message(string.format("%-4s  %-34s  %d silver%s",
            tostring(r.num), r.name, r.base_price, lev))
    end
    player:message(DIVIDER)
    player:message("Type CUSTOMIZE <#> to see material options for an item.")
    player:message("Type CUSTOMIZE <item#> <material#> <color> to select all at once, then CONFIRM.")
end

-- ── Show material list for a selected item ────────────────────────────────────
function Customize:_showMaterialList(player, item_row)
    player:message("")
    player:message("Materials available for: "..item_row.name)
    player:message(DIVIDER)
    player:message(string.format("%-4s  %-12s  %-18s  %s", "#", "Material", "Enchant", "Price"))
    player:message(SUB_DIV)
    for _, m in ipairs(Customize.MATERIALS) do
        local price    = self:_calcPrice(item_row.base_price, m)
        local enchant  = m.enchant > 0 and ("+"..m.enchant) or "none"
        local tooLow   = player:getLevel() < m.level
        local grayMark = tooLow and " *" or ""
        player:message(string.format("%-4s  %-12s  %-18s  %d silvers%s",
            tostring(m.id), m.name, enchant, price, grayMark))
    end
    player:message(DIVIDER)
    player:message("* Requires a higher level than you currently have.")
    player:message("Type CUSTOMIZE "..item_row.num.." <material#> <color>  then CONFIRM.")
    player:message("Color is optional.  Example: CUSTOMIZE "..item_row.num.." 5 silver")
end

-- ─────────────────────────────────────────────────────────────────────────────
-- CONFIRM – deduct silver, spawn timer, deliver item
-- ─────────────────────────────────────────────────────────────────────────────
function Customize:_cmdConfirm(player)
    local pid = player:getId()
    local st  = self._state[pid]

    if not st or st.confirmed then
        player:message("You don't have a pending order.  Type CUSTOMIZE to start one.")
        return true
    end

    -- Final silver check (player might have spent silver since CUSTOMIZE)
    if player:getSilver() < st.price then
        player:message(self.npc_name.." says, \"You seem to be short on silvers now.  Come back when you have "..st.price..".\"")
        self._state[pid] = nil
        return true
    end

    -- Mark confirmed to prevent double-spend
    st.confirmed = true

    -- Deduct silver
    player:deductSilver(st.price)

    local mat      = st.mat
    local item_row = st.item_row
    local colorStr = st.color
    local waitTime = mat.time_s  -- seconds

    -- Flavor message based on material tier
    local craftMsg
    if mat.enchant >= 30 then
        craftMsg = self.npc_name.." takes your silvers with a respectful bow. \""..
            "Crafting "..mat.name.." is no small task.  I'll have it ready shortly.\""
    elseif mat.enchant >= 20 then
        craftMsg = self.npc_name.." takes your silvers and rolls up their sleeves. \""..
            "Give me a few minutes with the "..mat.name..".\""
    else
        craftMsg = self.npc_name.." takes your silvers and moves to the workbench. \""..
            "Won't be long!\""
    end
    player:message(craftMsg)
    player:roomMessage(player:getName().." places a custom order with "..self.npc_name..".", player)

    -- Log the transaction
    DB.execute([[
        INSERT INTO transaction_log
            (character_id, transaction_type, item_id, silver_amount, notes)
        VALUES (?, 'item_customize', ?, ?, ?)
    ]], {
        pid,
        item_row.item_id,
        st.price,
        string.format("shop_id=%d mat=%s color=%s", self.shop_id, mat.name, colorStr or "none")
    })

    -- Schedule delivery
    local self_ref = self
    scheduleCallback(waitTime, function()
        self_ref:_deliverItem(player, st)
    end)

    -- Clear state AFTER scheduling (state still needed in closure above via st)
    self._state[pid] = nil

    return true
end

-- ─────────────────────────────────────────────────────────────────────────────
-- _deliverItem – called by timer callback
-- ─────────────────────────────────────────────────────────────────────────────
function Customize:_deliverItem(player, st)
    -- Player may have left; room-broadcast is fine either way
    local mat      = st.mat
    local item_row = st.item_row
    local colorStr = st.color

    -- Clone base item and override material/color/name
    local newItem = Items.clone(item_row.item_id)
    newItem:setMaterial(mat.name)
    if colorStr then
        newItem:setColor(colorStr)
    end
    if mat.enchant > 0 then
        newItem:setEnchantBonus(mat.enchant)
    end
    -- Build new display name: "a silver invar falchion" etc.
    local base = item_row.name:match("^%a+%s+(.-)%s*$") or item_row.name
    local prefix = colorStr and (colorStr.." "..mat.name) or mat.name
    newItem:setName("a "..prefix.." "..base)

    player:giveItem(newItem)

    player:message("")
    player:message(self.npc_name.." holds up "..newItem:getName().." and calls out, \""..player:getName()..", your order is ready!\"")
    player:roomMessage(self.npc_name.." calls out, \""..player:getName()..", your order is ready!\"")
end

return Customize
