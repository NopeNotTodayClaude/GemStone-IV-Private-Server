-- NPC: Savina
-- Auto-generated shopkeeper binding for room 13742
local NPC = {}
NPC.template_id    = "sol_savina_outfitting"
NPC.name           = "Savina"
NPC.article        = ""
NPC.title          = "clothier"
NPC.description    = "A stylish outfitter with a sharp eye for cut, drape, and wear."
NPC.home_room_id   = 13742
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
NPC.shop_id        = 351
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Savina nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper tidies a carefully arranged display.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
