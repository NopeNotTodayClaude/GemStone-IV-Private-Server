-- NPC: Frith
-- Zone/Town: auto-placed  |  Room: 1264
local NPC = {}

NPC.template_id    = "wl_frith_innkeeper"
NPC.name           = "Frith"
NPC.article        = ""
NPC.title          = "innkeeper"
NPC.description    = "A jovial heavyset man perpetually ready to listen to complaints about the weather."
NPC.home_room_id   = 1264

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
    default = "Frith doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
