---------------------------------------------------
-- clothier_vendara.lua
-- Ta'Vaalor Men's Clothier – Vendara (room 17292, shop 10)
--
-- Handles: ORDER, BUY, SELL, room entry greeting.
-- Delegates all heavy lifting to merchant_base.
---------------------------------------------------

local Merchant = require("npcs/merchants/merchant_base")

local npc = Merchant.new({
    shop_id  = 10,
    npc_name = "Vendara the clothier",
    entry_lines = {
        "Vendara the clothier smooths a bolt of fabric and glances up with a friendly nod.",
        "Vendara the clothier says, \"Good day!  Type ORDER to browse my selection, "
            .. "BUY # to purchase, or SELL <item> if you have something to trade.\"",
    },
    allow_sell = true,
    allow_buy  = true,
})

-- ── Event hooks ──────────────────────────────────────────────────────────────

function onPlayerEnter(player)
    npc:onEnter(player)
end

function onPlayerCommand(player, cmd, args)
    return npc:onCommand(player, cmd, args)
end

return npc
