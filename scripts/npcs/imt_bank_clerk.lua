-- NPC: a bank clerk
-- Zone/Town: auto-placed  |  Room: 3370
local NPC = {}

NPC.template_id    = "imt_bank_clerk"
NPC.name           = "a bank clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A round-faced halfling bundled in a thick wool coat handling silver cheerfully."
NPC.home_room_id   = 3370

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
    default = "a bank clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
