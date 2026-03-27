-- NPC: an elderly shopkeeper
-- Auto-generated shopkeeper binding for room 10916
local NPC = {}
NPC.template_id    = "rr_general_storekeeper"
NPC.name           = "an elderly shopkeeper"
NPC.article        = "an"
NPC.title          = "shopkeeper"
NPC.description    = "An elderly shopkeeper who watches customers over narrow spectacles with professional patience."
NPC.home_room_id   = 10916
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
NPC.shop_id        = 380
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "an elderly shopkeeper nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper glances over the shelves and makes a small adjustment.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
