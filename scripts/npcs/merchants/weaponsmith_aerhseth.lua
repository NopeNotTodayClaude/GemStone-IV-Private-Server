---------------------------------------------------
-- weaponsmith_aerhseth.lua
-- The Ta'Vaalor Weaponry – Aerhseth the weaponsmith (room 10367, shop 1)
--
-- Commands:
--   ORDER / LIST                         – browse base inventory (merchant_base)
--   BUY # / BUY <n>                      – buy standard (non-custom) item
--   SELL <item>                          – sell an item
--   CUSTOMIZE                            – show customizable item list + instructions
--   CUSTOMIZE <item#>                    – show material options for that item
--   CUSTOMIZE <item#> <mat#>             – select item + material
--   CUSTOMIZE <item#> <mat#> <color>     – full one-shot selection
--   CONFIRM  (or bare BUY after CUSTOMIZE) – place the order, start timer
---------------------------------------------------

local Merchant  = require("npcs/merchants/merchant_base")
local Customize = require("globals/utils/customize_system")

-- Standard shop (ORDER / BUY / SELL)
local merchant = Merchant.new({
    shop_id  = 1,
    npc_name = "Aerhseth the weaponsmith",
    entry_lines = {
        "Aerhseth the weaponsmith looks up from the grinding wheel with a brief nod.",
        "Aerhseth says, \"Weapons of all kinds.  Type ORDER to browse, BUY # to purchase, "
            .. "CUSTOMIZE to have something made to order, or SELL <item> to trade.\"",
    },
    allow_sell = true,
    allow_buy  = true,
})

-- Customization handler (same shop_id)
local customizer = Customize.new({
    shop_id  = 1,
    npc_name = "Aerhseth the weaponsmith",
})

-- ── Event hooks ──────────────────────────────────────────────────────────────

function onPlayerEnter(player)
    merchant:onEnter(player)
end

function onPlayerCommand(player, cmd, args)
    -- Customize commands take priority over standard BUY
    if cmd == "CUSTOMIZE" or cmd == "CONFIRM" then
        return customizer:onCommand(player, cmd, args)
    end

    -- Bare BUY with no args → check for pending customize order first
    if cmd == "BUY" and (not args or args == "") then
        if customizer:onCommand(player, cmd, args) then
            return true
        end
    end

    -- Standard merchant commands
    return merchant:onCommand(player, cmd, args)
end

