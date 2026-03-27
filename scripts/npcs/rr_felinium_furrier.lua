-- NPC: Felinium
-- Auto-generated shopkeeper binding for room 10934
local NPC = {}
NPC.template_id    = "rr_felinium_furrier"
NPC.name           = "Felinium"
NPC.article        = ""
NPC.title          = "furrier"
NPC.description    = "A trader with a sharp eye for quality pelts and travel-ready gear."
NPC.home_room_id   = 10934
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
NPC.shop_id        = 383
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Felinium nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper tidies a carefully arranged display.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
