-- NPC: a passing traveler
-- Zone/Town: auto-placed  |  Room: 10302
local NPC = {}

NPC.template_id    = "tv_passing_traveler"
NPC.name           = "a passing traveler"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A road-dusty traveler consulting a worn map with a furrowed brow."
NPC.home_room_id   = 10302

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
    road = "Ta'Vaalor roads are easier to follow than some maps make them look.",
    travel = "I have been told three different shortcuts today and trust none of them.",
    city = "Fine city.  Very orderly.  Makes a traveler suddenly aware of their own dust.",
    default = "The traveler folds the map slightly smaller.  'If you're giving directions, use landmarks.'",
}
NPC.ambient_emotes = {
    "The traveler turns the map sideways, then upside down, and finally back again.",
    "The traveler glances up from the map to compare it against the street ahead.",
    "The traveler brushes road dust from one sleeve with limited success.",
    "The traveler traces a route on the map with one finger and nods to themselves.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
