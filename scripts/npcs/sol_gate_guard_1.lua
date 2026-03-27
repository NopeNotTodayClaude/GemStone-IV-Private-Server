-- NPC: a city guard
-- Zone/Town: auto-placed  |  Room: 1507
local NPC = {}

NPC.template_id    = "sol_gate_guard_1"
NPC.name           = "a city guard"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A uniformed guard watching the gate with professional attention."
NPC.home_room_id   = 1507

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
    default = "a city guard doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
