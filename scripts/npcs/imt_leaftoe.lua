-- NPC: Leaftoe
-- Zone/Town: auto-placed  |  Room: 3363
local NPC = {}

NPC.template_id    = "imt_leaftoe"
NPC.name           = "Leaftoe"
NPC.article        = ""
NPC.title          = "baker and herbalist"
NPC.description    = "A bustling halfling who bakes bread and prepares herbal remedies simultaneously."
NPC.home_room_id   = 3363

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
    default = "Leaftoe doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
