-- NPC: a dwarven innkeeper
-- Auto-generated shopkeeper binding for room 9482
local NPC = {}
NPC.template_id    = "zl_inn_keeper_zl"
NPC.name           = "a dwarven innkeeper"
NPC.article        = "a"
NPC.title          = "innkeeper"
NPC.description    = "A loud jovial dwarf who runs the Bawdy Bard with more noise than management."
NPC.home_room_id   = 9482
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
NPC.shop_id        = 426
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "a dwarven innkeeper nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper straightens a few items behind the counter.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
