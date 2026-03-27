-- NPC: a jungle warrior
-- Zone/Town: auto-placed  |  Room: 23661
local NPC = {}

NPC.template_id    = "mh_warrior_sentry_mh"
NPC.name           = "a jungle warrior"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A lean warrior at the guild path entrance alert despite the relaxed island setting."
NPC.home_room_id   = 23661

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
    default = "a jungle warrior doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
