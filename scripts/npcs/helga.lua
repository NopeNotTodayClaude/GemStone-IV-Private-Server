-- NPC: Helga
-- Auto-generated shopkeeper binding for room 3809
local NPC = {}
NPC.template_id    = "helga"
NPC.name           = "Helga"
NPC.article        = ""
NPC.title          = "innkeeper"
NPC.description    = "A broad-smiled hostess who runs a busy tavern with the ease of long habit."
NPC.home_room_id   = 3809
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
NPC.shop_id        = 306
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Helga nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper straightens a few items behind the counter.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
