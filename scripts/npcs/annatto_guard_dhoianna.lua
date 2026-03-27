local NPC = {}

NPC.template_id    = "annatto_guard_dhoianna"
NPC.name           = "Dhoianna"
NPC.article        = ""
NPC.title          = "the bridge sentry"
NPC.description    = "A bridge sentry in spotless crimson whose alertness is softened only by an unexpectedly warm smile."
NPC.home_room_id   = 10494

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
    bridge = "The bridge gives us enough warning to greet the expected and question the rest.",
    neartofar = "Neartofar folk keep good schedules and better carts.  Usually.",
    default = "Dhoianna greets you with a calm, professional smile.",
}
NPC.ambient_emotes = {
    "Dhoianna watches the Annatto span with relaxed but constant attention.",
    "Dhoianna takes one measured step aside for a merchant cart and returns to her mark.",
    "Dhoianna glances back toward the gate as if checking an invisible timetable.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 95

return NPC
