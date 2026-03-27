---------------------------------------------------
-- clothier_raeliveth.lua
-- Ta'Vaalor Women's Clothier – Raeliveth (room 17293, shop 16)
--
-- Handles: ORDER, BUY, SELL, room entry greeting.
-- Delegates all heavy lifting to merchant_base.
---------------------------------------------------

local Merchant = require("npcs/merchants/merchant_base")

local npc = Merchant.new({
    shop_id  = 16,
    npc_name = "Raeliveth the clothier",
    entry_lines = {
        "Raeliveth the clothier looks up from a length of fabric with a welcoming smile.",
        "Raeliveth the clothier says, \"Welcome!  Type ORDER to browse my selection, "
            .. "BUY # to purchase, or SELL <item> if you have something to trade.\"",
    },
    allow_sell = true,
    allow_buy  = true,
})

-- ── Event hooks (called by your NPC/room event dispatcher) ───────────────────

-- Called when a player enters room 17293
function onPlayerEnter(player)
    npc:onEnter(player)
end

-- Called when a player types a command while in room 17293
-- Return true = command consumed; false = pass to normal handler
function onPlayerCommand(player, cmd, args)
    return npc:onCommand(player, cmd, args)
end

return npc
