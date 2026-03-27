local NPC = {}

NPC.template_id    = "vermilion_guard_rethustril"
NPC.name           = "Rethustril"
NPC.article        = ""
NPC.title          = "the bridge sentry"
NPC.description    = "A wiry sentry posted to the Vermilion Bridge, with a hooded cloak and a gaze that misses very little."
NPC.home_room_id   = 5828

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
    bridge = "The bridge gives me just enough distance to decide who deserves questions.",
    road = "Cemetery road has a way of draining cheer from the unprepared.",
    default = "Rethustril gives you a cool, appraising look and then a short nod.",
}
NPC.ambient_emotes = {
    "Rethustril peers over the bridge rail and listens to the wind below.",
    "Rethustril draws her cloak more tightly against a passing draft.",
    "Rethustril turns at the creak of a wagon axle and tracks it until it passes.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 95

return NPC
