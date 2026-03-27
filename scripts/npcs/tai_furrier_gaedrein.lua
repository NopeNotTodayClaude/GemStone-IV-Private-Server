-- NPC: Gaedrein
-- Auto-generated shopkeeper binding for room 4019
local NPC = {}
NPC.template_id    = "tai_furrier_gaedrein"
NPC.name           = "Gaedrein"
NPC.article        = ""
NPC.title          = "furrier"
NPC.description    = "A patient furrier who inspects every hide like a jeweler studying a stone."
NPC.home_room_id   = 4019
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
NPC.shop_id        = 323
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Gaedrein nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper tidies a carefully arranged display.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
