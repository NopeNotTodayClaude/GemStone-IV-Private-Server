-- NPC: Nagrek
-- Zone/Town: auto-placed  |  Room: 1886
local NPC = {}

NPC.template_id    = "ti_nagrek"
NPC.name           = "Nagrek"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A grizzled dwarven veteran running the company store pelt section."
NPC.home_room_id   = 1886

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
    default = "Nagrek doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
