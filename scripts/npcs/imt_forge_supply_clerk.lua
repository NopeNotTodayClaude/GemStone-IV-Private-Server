-- NPC: a forge clerk
-- Auto-generated shopkeeper binding for room 9007
local NPC = {}
NPC.template_id    = "imt_forge_supply_clerk"
NPC.name           = "a forge clerk"
NPC.article        = "a"
NPC.title          = "supply clerk"
NPC.description    = "A frost-hardened clerk who keeps forge stock sorted by both price and practicality."
NPC.home_room_id   = 9007
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
NPC.shop_id        = 368
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "a forge clerk nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper checks over the goods with practiced efficiency.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
