-- NPC: a cafe keeper
-- Auto-generated shopkeeper binding for room 32582
local NPC = {}
NPC.template_id    = "rr_tridents_voyage_keeper"
NPC.name           = "a cafe keeper"
NPC.article        = "a"
NPC.title          = "innkeeper"
NPC.description    = "A relaxed keeper who serves travelers as though they were already regulars."
NPC.home_room_id   = 32582
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
NPC.shop_id        = 394
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "a cafe keeper nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper straightens a few items behind the counter.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
