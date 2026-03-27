-- NPC: Kaldonis
-- Auto-generated shopkeeper binding for room 24470
local NPC = {}
NPC.template_id    = "rr_kaldonis_outfitting"
NPC.name           = "Kaldonis"
NPC.article        = ""
NPC.title          = "clothier"
NPC.description    = "A shrewd outfitter whose wares look chosen for both road and harbor."
NPC.home_room_id   = 24470
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
NPC.shop_id        = 393
NPC.dialogues = {
    buy = "Use LIST to review the stock, then BUY what you want.",
    sell = "Show me what you're parting with and I'll see what it's worth.",
    list = "Use LIST to review the stock, then BUY what you want.",
    default = "Kaldonis nods toward the stock.  'Use LIST to see what's available.'",
}
NPC.ambient_emotes = {
    "The shopkeeper tidies a carefully arranged display.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
return NPC
