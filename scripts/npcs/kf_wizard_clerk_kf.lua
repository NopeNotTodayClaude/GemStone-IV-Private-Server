-- NPC: a wizard guild clerk
-- Zone/Town: auto-placed  |  Room: 28885
local NPC = {}

NPC.template_id    = "kf_wizard_clerk_kf"
NPC.name           = "a wizard guild clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A scholar managing the wizard guild's island outpost."
NPC.home_room_id   = 28885

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
    default = "a wizard guild clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
