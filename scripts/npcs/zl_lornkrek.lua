-- NPC: Lornkrek
-- Zone/Town: auto-placed  |  Room: 9477
local NPC = {}

NPC.template_id    = "zl_lornkrek"
NPC.name           = "Lornkrek"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A scarred dwarven veteran who now manages inventory at Hortemeyer's shop."
NPC.home_room_id   = 9477

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
    default = "Lornkrek doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
