local NPC = {}

NPC.template_id    = "amaranth_guard_raerselim"
NPC.name           = "Raerselim"
NPC.article        = ""
NPC.title          = "the bridge sentry"
NPC.description    = "A spare-built elven sentry with steady hands and the focused expression of someone always counting exits."
NPC.home_room_id   = 6104

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
    bridge = "The bridge is where you sort haste from panic.",
    road = "People headed out move one way.  People regretting it move another.",
    default = "Raerselim acknowledges you with a measured glance and a nod.",
}
NPC.ambient_emotes = {
    "Raerselim studies the far end of the bridge without blinking for several long seconds.",
    "Raerselim draws a slow breath and settles more firmly into place.",
    "Raerselim lifts two fingers in a quiet signal to a guard at the gate.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 95

return NPC
