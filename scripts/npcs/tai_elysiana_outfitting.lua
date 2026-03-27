-- NPC: Elysiana
-- Auto-generated shopkeeper binding for room 5036
local NPC = {}
NPC.template_id    = "tai_elysiana_outfitting"
NPC.name           = "Elysiana"
NPC.article        = ""
NPC.title          = "clothier"
NPC.description    = "A poised clothier who judges thread count with one touch and never guesses twice."
NPC.home_room_id   = 5036
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
NPC.shop_id        = 332
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Elysiana nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper tidies a carefully arranged display.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
