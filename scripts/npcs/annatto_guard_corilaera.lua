local NPC = {}

NPC.template_id    = "annatto_guard_corilaera"
NPC.name           = "Corilaera"
NPC.article        = ""
NPC.title          = "the Legion guardsman"
NPC.description    = "A quiet elven guardswoman with bright, alert eyes and an utterly composed stance."
NPC.home_room_id   = 5906

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
    gate = "Annatto handles more routine days than memorable ones.  We like it that way.",
    road = "A calm road is still worth watching.",
    default = "Corilaera offers a brief nod and keeps scanning the approach.",
}
NPC.ambient_emotes = {
    "Corilaera turns her head toward a distant cart and judges its pace at a glance.",
    "Corilaera rests her spear butt more firmly against the paving stones.",
    "Corilaera exchanges a quiet glance with Daervith and returns to stillness.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 90

return NPC
