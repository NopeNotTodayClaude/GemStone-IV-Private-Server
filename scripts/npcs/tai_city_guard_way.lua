-- NPC: an Illistim city guard
-- Zone/Town: auto-placed  |  Room: 714
local NPC = {}

NPC.template_id    = "tai_city_guard_way"
NPC.name           = "an Illistim city guard"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "A patrol guard moving through the wey with measured steps."
NPC.home_room_id   = 714

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
    default = "an Illistim city guard doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
