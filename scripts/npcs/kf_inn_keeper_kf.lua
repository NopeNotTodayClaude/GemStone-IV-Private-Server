-- NPC: a sea hag innkeeper
-- Zone/Town: auto-placed  |  Room: 28947
local NPC = {}

NPC.template_id    = "kf_inn_keeper_kf"
NPC.name           = "a sea hag innkeeper"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A weathered woman who runs the Sea Hag's Roost with ruthless hospitality."
NPC.home_room_id   = 28947

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
    default = "a sea hag innkeeper doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
