-- NPC: a town guard
-- Zone/Town: auto-placed  |  Room: 3424
local NPC = {}

NPC.template_id    = "imt_nightowl_guard"
NPC.name           = "a town guard"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A stocky halfling in city livery scanning the pub's patrons for trouble."
NPC.home_room_id   = 3424

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
    default = "a town guard doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
