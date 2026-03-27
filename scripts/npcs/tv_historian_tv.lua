-- NPC: a city historian
-- Zone/Town: auto-placed  |  Room: 10441
local NPC = {}

NPC.template_id    = "tv_historian_tv"
NPC.name           = "a city historian"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A studious elven historian surrounded by carefully annotated documents."
NPC.home_room_id   = 10441

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
    history = "Ta'Vaalor keeps history in archives, walls, and the habits no one remembers choosing.",
    war = "Military history is mostly logistics interrupted by courage.",
    court = "Victory Court is a fine place to study continuity.  People change.  Processions do not.",
    default = "The historian looks up from a page margin full of notes.  'If you want the short version, ask a bard.'",
}
NPC.ambient_emotes = {
    "The historian compares two documents line by line with patient concentration.",
    "The historian underlines a passage, then adds an even smaller note beneath it.",
    "The historian pauses to consider the square outside before returning to the text.",
    "The historian arranges a stack of annotated papers into a more exact order.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
