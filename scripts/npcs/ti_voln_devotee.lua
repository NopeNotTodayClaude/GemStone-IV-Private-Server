-- NPC: a Voln devotee
-- Zone/Town: auto-placed  |  Room: 1983
local NPC = {}

NPC.template_id    = "ti_voln_devotee"
NPC.name           = "a Voln devotee"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A quiet dwarf in a meditation sanctum who nods respectfully at those who enter."
NPC.home_room_id   = 1983

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
    default = "a Voln devotee doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
