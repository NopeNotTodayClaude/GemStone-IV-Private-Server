-- NPC: Dhoianna
-- Zone/Town: auto-placed  |  Room: 640
local NPC = {}

NPC.template_id    = "tai_dhoianna"
NPC.name           = "Dhoianna"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A silver-haired elven woman browsing the herbalist's wares with expert attention."
NPC.home_room_id   = 640

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
    default = "Dhoianna doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
