-- NPC: a furrier
-- Zone/Town: auto-placed  |  Room: 35238
local NPC = {}

NPC.template_id    = "sab_furrier_sab"
NPC.name           = "a furrier"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A merchant at Skins and Grins with a wide selection and few questions."
NPC.home_room_id   = 35238

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
    default = "a furrier doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
