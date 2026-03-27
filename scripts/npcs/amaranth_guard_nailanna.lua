local NPC = {}

NPC.template_id    = "amaranth_guard_nailanna"
NPC.name           = "Nailanna"
NPC.article        = ""
NPC.title          = "the bridge sentry"
NPC.description    = "A sharp-eyed sentry with a burnished helm tucked under one arm and a habit of listening before speaking."
NPC.home_room_id   = 6103

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
    bridge = "Bridges tell the truth about wagons and nerves in equal measure.",
    traffic = "Most of my work is deciding what matters before it reaches the gate.",
    default = "Nailanna watches you cross the bridge and inclines her head.",
}
NPC.ambient_emotes = {
    "Nailanna turns her head toward a sound below the bridge and listens for a moment.",
    "Nailanna checks the lashings on a nearby supply cart with quick efficiency.",
    "Nailanna lifts her helm, studies its strap, and tucks it beneath one arm again.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 95

return NPC
