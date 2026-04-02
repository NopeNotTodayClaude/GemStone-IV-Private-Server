-- NPC: a Vaalor innkeeper
-- Zone/Town: Ta'Vaalor Inns  |  Room: 10385
local NPC = {}

NPC.template_id    = "tv_malwith_innkeeper"
NPC.name           = "a Vaalor innkeeper"
NPC.article        = "a"
NPC.title          = "innkeeper"
NPC.description    = "An immaculate Vaalor host stands behind the desk with a ledger close at hand and the crisp composure of someone who tolerates no disorder in his inn."
NPC.home_room_id   = 10385

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    default = "The Vaalor innkeeper says, \"CHECK IN at the desk if you mean to stay.  Ask about a room or a table once you are registered.\"",
}

NPC.ambient_emotes = {
    "The innkeeper straightens a stack of room ledgers and smooths the edge of the desk.",
    "The innkeeper adjusts a brass key tag, then looks up with reserved patience.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
