-- NPC: Furryback
-- Zone/Town: auto-placed  |  Room: 2466
local NPC = {}

NPC.template_id    = "imt_furryback"
NPC.name           = "Furryback"
NPC.article        = ""
NPC.title          = "pelt trader"
NPC.description    = "A large halfling with an impressive fur-lined coat and the smell of the wilderness about him."
NPC.home_room_id   = 2466

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
    default = "Furryback doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
