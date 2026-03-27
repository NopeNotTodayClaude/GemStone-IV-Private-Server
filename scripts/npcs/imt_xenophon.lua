-- NPC: Xenophon
-- Auto-generated shopkeeper binding for room 3451
local NPC = {}
NPC.template_id    = "imt_xenophon"
NPC.name           = "Xenophon"
NPC.article        = ""
NPC.title          = "master bowyer"
NPC.description    = "An aged halfling whose trembling hands become perfectly steady the moment he picks up a bow."
NPC.home_room_id   = 3451
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
NPC.shop_id        = 365
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Xenophon nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper checks over the goods with practiced efficiency.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
