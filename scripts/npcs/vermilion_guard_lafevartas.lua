local NPC = {}

NPC.template_id    = "vermilion_guard_lafevartas"
NPC.name           = "Lafevartas"
NPC.article        = ""
NPC.title          = "the Legion guardsman"
NPC.description    = "A tall Vaalor soldier whose stern face softens only when nobody is directly looking at him."
NPC.home_room_id   = 5827

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
    duty = "The city's calm depends on somebody taking ugly roads seriously.",
    sassion = "If Sassion sends you out with a task, finish it before she invents two more.",
    default = "Lafevartas flicks a glance your way and nods once.",
}
NPC.ambient_emotes = {
    "Lafevartas shifts his stance and watches the gate from under lowered brows.",
    "Lafevartas listens to a distant sound from the bridge, then relaxes fractionally.",
    "Lafevartas checks the set of a leather strap on his shield arm.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 90

return NPC
