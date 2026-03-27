-- NPC: Krythussa
-- Auto-generated shopkeeper binding for room 386
local NPC = {}
NPC.template_id    = "wl_krythussa_baker"
NPC.name           = "Krythussa"
NPC.article        = ""
NPC.title          = "baker"
NPC.description    = "A flour-dusted confectioner who keeps trays of sweets lined up with military precision."
NPC.home_room_id   = 386
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
NPC.shop_id        = 311
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Krythussa nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper straightens a few items behind the counter.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
