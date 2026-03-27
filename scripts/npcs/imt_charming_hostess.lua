-- NPC: a charming halfling hostess
-- Zone/Town: auto-placed  |  Room: 3427
local NPC = {}

NPC.template_id    = "imt_charming_hostess"
NPC.name           = "a charming halfling hostess"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A bright-eyed halfling who greets every guest as if they are the most important arrival of the day."
NPC.home_room_id   = 3427

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
    default = "a charming halfling hostess doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
