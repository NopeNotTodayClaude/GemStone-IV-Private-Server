-- NPC: Calikran
-- Zone/Town: auto-placed  |  Room: 223
local NPC = {}

NPC.template_id    = "wl_calikran"
NPC.name           = "Calikran"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A hawk-faced merchant who appraises everyone he meets as a potential customer."
NPC.home_room_id   = 223

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
    default = "Calikran doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
