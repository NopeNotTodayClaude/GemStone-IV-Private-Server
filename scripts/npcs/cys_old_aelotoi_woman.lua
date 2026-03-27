-- NPC: an old aelotoi woman
-- Zone/Town: auto-placed  |  Room: 4647
local NPC = {}

NPC.template_id    = "cys_old_aelotoi_woman"
NPC.name           = "an old aelotoi woman"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "An elderly aelotoi whose folded wings and quiet manner suggest long years of experience."
NPC.home_room_id   = 4647

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
    default = "an old aelotoi woman doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
