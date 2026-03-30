local NPC = {}

NPC.template_id    = "tv_rogue_iron_door_sentry"
NPC.name           = "a heavily armed sentry"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A heavily armed elf standing watch beside the reinforced iron door, alert without seeming eager to prove it."
NPC.home_room_id   = 17829

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
    door = "That door stays barred unless the guild says otherwise.",
    guards = "The inn side remains quiet because we keep it that way.",
    default = "The sentry's attention never strays far from the reinforced door.",
}
NPC.ambient_emotes = {
    "The heavily armed sentry shifts weight without taking her eyes off the barred door.",
    "The heavily armed sentry glances toward the sign above the door and then back down the hall.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45

return NPC
