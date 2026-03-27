local NPC = {}

NPC.template_id    = "victory_guard_gaelthar"
NPC.name           = "Gaelthar"
NPC.article        = ""
NPC.title          = "the bridge sentry"
NPC.description    = "A lean Vaalor sentry whose polished mail and wind-creased face suggest equal respect for regulation and weather."
NPC.home_room_id   = 5948

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
    bridge = "The bridge is where nervous travelers show their nerves and tired wagons show their flaws.",
    south = "Past the bridge, the city ends and excuses stop mattering.",
    default = "Gaelthar glances along the span and gives you a measured nod.",
}
NPC.ambient_emotes = {
    "Gaelthar leans slightly into the wind and scans the bridge from end to end.",
    "Gaelthar checks the fit of a leather strap securing his shield.",
    "Gaelthar turns at the creak of wagon wheels and watches until the sound passes.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 95

return NPC
