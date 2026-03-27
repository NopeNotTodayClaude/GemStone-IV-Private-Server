-- NPC: an elven merchant
-- Zone/Town: auto-placed  |  Room: 3542
local NPC = {}

NPC.template_id    = "generic_elven_merchant"
NPC.name           = "an elven merchant"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "An elven merchant going about daily business with practiced composure."
NPC.home_room_id   = 3542

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
    default = "an elven merchant doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
