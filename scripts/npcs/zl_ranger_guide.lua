-- NPC: a ranger guide
-- Zone/Town: auto-placed  |  Room: 9441
local NPC = {}

NPC.template_id    = "zl_ranger_guide"
NPC.name           = "a ranger guide"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A gnome ranger offering guidance through the winding tunnels."
NPC.home_room_id   = 9441

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
    default = "a ranger guide doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
