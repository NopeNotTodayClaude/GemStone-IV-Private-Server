-- NPC: Kahlyr
-- Auto-generated shopkeeper binding for room 5719
local NPC = {}
NPC.template_id    = "sol_kahlyr_jeweler"
NPC.name           = "Kahlyr"
NPC.article        = ""
NPC.title          = "jeweler"
NPC.description    = "A jeweler whose appreciative glance weighs a stone before his hands ever touch it."
NPC.home_room_id   = 5719
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
NPC.shop_id        = 346
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Kahlyr nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper tidies a carefully arranged display.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
