-- NPC: Brother Barnstel
-- Zone/Town: auto-placed  |  Room: 9505
local NPC = {}

NPC.template_id    = "zl_herbalist_barnstel"
NPC.name           = "Brother Barnstel"
NPC.article        = ""
NPC.title          = "herbalist monk"
NPC.description    = "A round-faced dwarven monk tending his underground herb garden with monastic care."
NPC.home_room_id   = 9505

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
    default = "Brother Barnstel doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
