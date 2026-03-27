-- NPC: Berrytoe
-- Auto-generated shopkeeper binding for room 2424
local NPC = {}
NPC.template_id    = "imt_berrytoe_shopkeeper"
NPC.name           = "Berrytoe"
NPC.article        = ""
NPC.title          = "shopkeeper"
NPC.description    = "A halfling merchant whose shelves are packed with the sort of practical goods every traveler eventually needs."
NPC.home_room_id   = 2424
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
NPC.shop_id        = 360
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Berrytoe nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper glances over the shelves and makes a small adjustment.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
