local NPC = {}

NPC.template_id    = "vermilion_guard_ridtha"
NPC.name           = "Ridtha"
NPC.article        = ""
NPC.title          = "the bridge sentry"
NPC.description    = "A compact elven sentry with clipped movements and a stare sharpened by long bridge watches."
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
    watch = "Bridge duty is mostly attention and the moments when attention suddenly matters.",
    undead = "Anything that comes shambling this way had better be ready to stop.",
    default = "Ridtha gives the faintest tilt of her head in greeting.",
}
NPC.ambient_emotes = {
    "Ridtha shifts her grip on her spear and resumes her exact stance.",
    "Ridtha watches the gateward traffic with a hard, practical stare.",
    "Ridtha glances toward Vermilion Gate as though confirming all remains in order.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 95

return NPC
