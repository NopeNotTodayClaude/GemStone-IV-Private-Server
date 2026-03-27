local NPC = {}

NPC.template_id    = "amaranth_guard_ariyr"
NPC.name           = "Ariyr"
NPC.article        = ""
NPC.title          = "the Legion guardsman"
NPC.description    = "A severe-faced Vaalor guardsman with immaculate armor and a gaze sharpened by long habit."
NPC.home_room_id   = 3727

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
    gate = "Amaranth has stood longer than most arguments about how best to guard it.",
    road = "The road is kindest to people who respect where it leads.",
    default = "Ariyr acknowledges you with a short, disciplined nod.",
}
NPC.ambient_emotes = {
    "Ariyr inspects the gate hinges with an eye trained to catch tiny faults.",
    "Ariyr looks over a passing wagon and dismisses it with a faint exhale.",
    "Ariyr folds his hands behind his back and resumes his exact stance.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 90

return NPC
