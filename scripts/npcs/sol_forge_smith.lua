-- NPC: a forge master
-- Zone/Town: auto-placed  |  Room: 5039
local NPC = {}

NPC.template_id    = "sol_forge_smith"
NPC.name           = "a forge master"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A powerfully built smith who coordinates work across the metalworking platforms."
NPC.home_room_id   = 5039

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
    default = "a forge master doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
