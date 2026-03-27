-- NPC: a United Bank clerk
-- Zone/Town: auto-placed  |  Room: 11
local NPC = {}

NPC.template_id    = "tai_bank_clerk"
NPC.name           = "a United Bank clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An immaculate elven teller who handles transactions with aristocratic composure."
NPC.home_room_id   = 11

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
    default = "a United Bank clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
