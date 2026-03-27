local NPC = {}

NPC.template_id    = "victory_guard_dukash"
NPC.name           = "Dukash"
NPC.article        = ""
NPC.title          = "the Legion guardsman"
NPC.description    = "A dark-haired Vaalor soldier with a square stance and a faintly skeptical expression worn into his features."
NPC.home_room_id   = 5907

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
    gate = "The gate works best when travelers answer the first question instead of the third.",
    hunting = "If you're going south to hunt, come back with the same number of companions you left with.",
    default = "Dukash grunts once in acknowledgment and keeps his eyes on the gate traffic.",
}
NPC.ambient_emotes = {
    "Dukash adjusts the fall of his crimson cloak with a short, economical motion.",
    "Dukash narrows his eyes at a distant shape on the road until it resolves into a harmless wagon.",
    "Dukash taps two fingers lightly against his spear shaft and stills them at once.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 90

return NPC
