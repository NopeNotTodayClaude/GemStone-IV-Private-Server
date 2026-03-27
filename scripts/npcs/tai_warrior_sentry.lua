-- NPC: an Illistim warrior
-- Zone/Town: auto-placed  |  Room: 13307
local NPC = {}

NPC.template_id    = "tai_warrior_sentry"
NPC.name           = "an Illistim warrior"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "An elven warrior at the guild entrance maintaining formal posture."
NPC.home_room_id   = 13307

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
    default = "an Illistim warrior doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
