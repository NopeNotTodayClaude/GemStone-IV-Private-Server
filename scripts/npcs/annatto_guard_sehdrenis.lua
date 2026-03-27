local NPC = {}

NPC.template_id    = "annatto_guard_sehdrenis"
NPC.name           = "Sehdrenis"
NPC.article        = ""
NPC.title          = "the bridge sentry"
NPC.description    = "A long-limbed elven sentry whose easy balance and constant watchfulness make the post look effortless."
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
    watch = "Bridge work is simpler than gate work and more deceptive for it.",
    trade = "You learn a lot about trade from the look of a driver's shoulders.",
    default = "Sehdrenis inclines his head and keeps his attention on the bridge.",
}
NPC.ambient_emotes = {
    "Sehdrenis braces one hand on the bridge rail and scans the road beyond.",
    "Sehdrenis listens to the clatter of approaching wheels and judges the load by ear.",
    "Sehdrenis settles back into stillness after a brief exchange with Dhoianna.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 95

return NPC
