-- NPC: a snowbound traveler
-- Zone/Town: auto-placed  |  Room: 3411
local NPC = {}

NPC.template_id    = "imt_snowbound_traveler"
NPC.name           = "a snowbound traveler"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A heavily bundled figure stamping snow from their boots and asking about the road south."
NPC.home_room_id   = 3411

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
    default = "a snowbound traveler doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
