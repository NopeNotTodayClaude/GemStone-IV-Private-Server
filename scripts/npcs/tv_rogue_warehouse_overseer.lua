local NPC = {}

NPC.template_id    = "tv_rogue_warehouse_overseer"
NPC.name           = "a well-dressed overseer"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A well-dressed elf with immaculate cuffs and the alert posture of someone who notices every misplaced crate and every misplaced rogue."
NPC.home_room_id   = 17820

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
    repairs = "The guild fixes what keeps it useful and abandons what does not.",
    warehouse = "This floor stores more than crates.  It stores things the guild wants close at hand and closer to silence.",
    default = "The overseer gives the room another careful look before acknowledging you.",
}
NPC.ambient_emotes = {
    "The well-dressed overseer gestures toward one corner of the warehouse and murmurs a correction to no one in particular.",
    "The well-dressed overseer checks the fit of a nearby doorframe with a critical eye.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45

return NPC
