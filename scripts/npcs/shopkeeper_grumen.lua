-- NPC: Shopkeeper Grumen
-- Auto-generated shopkeeper binding for room 9493
local NPC = {}
NPC.template_id    = "shopkeeper_grumen"
NPC.name           = "Shopkeeper Grumen"
NPC.article        = ""
NPC.title          = "shopkeeper"
NPC.description    = "A dwarven shopkeeper whose inventory of tunnel essentials is comprehensive."
NPC.home_room_id   = 9493
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
NPC.shop_id        = 420
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Shopkeeper Grumen nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper glances over the shelves and makes a small adjustment.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
