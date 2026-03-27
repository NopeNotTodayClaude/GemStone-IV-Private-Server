-- NPC: Valina
-- Auto-generated shopkeeper binding for room 640
local NPC = {}
NPC.template_id    = "tai_herbalist_valina"
NPC.name           = "Valina"
NPC.article        = ""
NPC.title          = "herbalist"
NPC.description    = "A graceful elven herbalist whose shop carries herbs from across the continent."
NPC.home_room_id   = 640
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
NPC.shop_id        = 324
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Valina nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper tidies a carefully arranged display.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
