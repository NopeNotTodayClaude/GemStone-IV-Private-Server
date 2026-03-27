local NPC = {}

NPC.template_id    = "victory_guard_simlasyth"
NPC.name           = "Simlasyth"
NPC.article        = ""
NPC.title          = "the bridge sentry"
NPC.description    = "A keen-eyed elven sentry with a traveler-counting habit and a posture too straight to be accidental."
NPC.home_room_id   = 3549

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
    patrol = "Bridge duty sounds dull until you realize how many things can go wrong in one narrow place.",
    city = "From here you can hear Ta'Vaalor breathing if you know the sound of it.",
    default = "Simlasyth offers a crisp salute with two fingers to her brow.",
}
NPC.ambient_emotes = {
    "Simlasyth watches the city side of the bridge with cool, attentive focus.",
    "Simlasyth shifts her spear to her other hand without breaking posture.",
    "Simlasyth steps aside for a cart to pass and returns to her mark exactly.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 95

return NPC
