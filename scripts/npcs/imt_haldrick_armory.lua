-- NPC: Haldrick
-- Auto-generated shopkeeper binding for room 3455
local NPC = {}
NPC.template_id    = "imt_haldrick_armory"
NPC.name           = "Haldrick"
NPC.article        = ""
NPC.title          = "armorer"
NPC.description    = "A rugged armorer who stocks gear fit for snow, wind, and bad decisions."
NPC.home_room_id   = 3455
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
NPC.shop_id        = 362
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Haldrick nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper checks over the goods with practiced efficiency.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
