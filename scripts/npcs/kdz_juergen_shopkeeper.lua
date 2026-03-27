-- NPC: Juergen
-- Auto-generated shopkeeper binding for room 14740
local NPC = {}
NPC.template_id    = "kdz_juergen_shopkeeper"
NPC.name           = "Juergen"
NPC.article        = ""
NPC.title          = "shopkeeper"
NPC.description    = "A broad-shouldered dwarven merchant whose stock reflects long familiarity with volcanic travel."
NPC.home_room_id   = 14740
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
NPC.shop_id        = 440
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Juergen nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper glances over the shelves and makes a small adjustment.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
