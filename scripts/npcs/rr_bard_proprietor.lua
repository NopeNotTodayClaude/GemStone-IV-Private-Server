-- NPC: a bard proprietor
-- Zone/Town: auto-placed  |  Room: 10879
local NPC = {}

NPC.template_id    = "rr_bard_proprietor"
NPC.name           = "a bard proprietor"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A musical halfling who manages the Plaza of Stars with cheerful enthusiasm."
NPC.home_room_id   = 10879

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
    default = "a bard proprietor doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
