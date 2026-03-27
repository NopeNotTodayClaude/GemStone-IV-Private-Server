-- NPC: a consignment clerk
-- Auto-generated shopkeeper binding for room 11004
local NPC = {}
NPC.template_id    = "rr_lomara_consignor"
NPC.name           = "a consignment clerk"
NPC.article        = "a"
NPC.title          = "shop clerk"
NPC.description    = "A sharp-eyed clerk who handles secondhand stock with the wary care of someone who has seen what people try to sell."
NPC.home_room_id   = 11004
NPC.can_combat     = false
NPC.can_shop       = true
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false
NPC.shop_id        = 390
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "a consignment clerk nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper glances over the shelves and makes a small adjustment.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
