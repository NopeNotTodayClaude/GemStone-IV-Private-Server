local NPC = {}

NPC.template_id    = "victory_guard_arnlis"
NPC.name           = "Arnlis"
NPC.article        = ""
NPC.title          = "the Legion guardsman"
NPC.description    = "A broad-shouldered Vaalor guardsman with a scar running from temple to jaw and the patient stare of a veteran road watcher."
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
    road = "Victory Road stays manageable if people remember the wilderness owes them nothing.",
    legion = "The Legion prefers gates staffed by soldiers who know how to wait without dozing.",
    default = "Arnlis gives you a brief nod and returns his attention to the road.",
}
NPC.ambient_emotes = {
    "Arnlis rests one gauntleted hand on the pommel of his sword and studies the road.",
    "Arnlis glances along the gate wall, checking each angle with practiced care.",
    "Arnlis exchanges a low word with Laerindra and resumes his watch.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 90

return NPC
