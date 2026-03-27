-- NPC: a ranger guide
-- Zone/Town: auto-placed  |  Room: 9441
local NPC = {}

NPC.template_id    = "zl_ranger_guide"
NPC.name           = "a ranger guide"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A gnome ranger offering guidance through the winding tunnels."
NPC.home_room_id   = 24367

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = true
NPC.can_loot       = false
NPC.is_guild       = true
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    ranger = "The Ranger Guild favors fieldcraft over boasting.  Learn the land and it will answer you in turn.",
    join = "Once you have the experience to qualify, the guild can take your name and start your training.",
    training = "A ranger advances through stealth, lore, and the practical business of surviving in wild places.",
    forage = "Useful signs are everywhere when you stop stomping past them.",
    default = "The ranger guide nods once.  'Need the guild, do you?'",
}
NPC.ambient_emotes = {
    "The ranger guide glances over the room as if checking wind and trail at the same time.",
    "The ranger guide runs a thumb across the edge of a weathered field map.",
    "The ranger guide adjusts a travel-worn cloak and studies the nearest doorway.",
}
NPC.ambient_chance = 0.025
NPC.emote_cooldown = 60
NPC.guild_id       = "ranger"

return NPC
