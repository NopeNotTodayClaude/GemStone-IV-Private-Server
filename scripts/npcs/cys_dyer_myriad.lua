-- NPC: a Fluttering Myriad clerk
-- Auto-generated shopkeeper binding for room 4675
local NPC = {}
NPC.template_id    = "cys_dyer_myriad"
NPC.name           = "a Fluttering Myriad clerk"
NPC.article        = "a"
NPC.title          = "master dyer"
NPC.description    = "An aelotoi dyer whose wing-pattern inspires many of the shop's signature color combinations."
NPC.home_room_id   = 4675
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
NPC.shop_id        = 408
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "a Fluttering Myriad clerk nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper tidies a carefully arranged display.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
