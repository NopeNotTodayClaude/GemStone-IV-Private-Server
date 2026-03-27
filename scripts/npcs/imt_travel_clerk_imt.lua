-- NPC: a travel clerk
-- Zone/Town: auto-placed  |  Room: 3411
local NPC = {}

NPC.template_id    = "imt_travel_clerk_imt"
NPC.name           = "a travel clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A brisk halfling coordinating travel arrangements with surprising organizational skill."
NPC.home_room_id   = 3411

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
    default = "a travel clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
