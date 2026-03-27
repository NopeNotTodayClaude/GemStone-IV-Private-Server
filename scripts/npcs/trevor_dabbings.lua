-- NPC: Trevor Dabbings
-- Source: GemStone IV Wiki / starter mentor guidance
local NPC = {}

NPC.template_id    = "trevor_dabbings"
NPC.name           = "Trevor Dabbings"
NPC.article        = ""
NPC.title          = "the town patriarch"
NPC.description    = "Well-dressed and comfortably seated, Trevor Dabbings has the air of a man long accustomed to being listened to.  His expression is mild, but there is nothing vague about his gaze."
NPC.home_room_id   = 9005   -- LICH 4043275

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = true
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = true
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.greeting       = "inclines his head with patrician ease.  'Settling into Trace, are you?'"
NPC.dialogues = {
    advice = "A new adventurer can do worse than learn the shape of a town before chasing glory.  I have a short lesson if you care to hear it.",
    lesson = "Use QUEST START trevor_dabbings_lesson and answer properly when I question you.",
    work = "If you mean honest town work, Clovertooth Hall still uses eager hands for messages.",
    bounty = "Halline at the Adventurer's Guild handles that sort of work.  I handle instruction.",
    default = "Trevor Dabbings folds his hands neatly.  'Ask what you mean to ask.'",
}
NPC.ambient_emotes = {
    "Trevor Dabbings smooths one cuff and surveys the room with measured calm.",
    "Trevor Dabbings taps a finger against the arm of his chair in patient thought.",
    "Trevor Dabbings gives a faint, knowing smile at some private recollection.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70
NPC.chat_interval  = 450
NPC.chat_chance    = 0.11
NPC.chat_lines = {
    "Good habits earn a longer career than bravado.",
    "Trace looks gentle until you meet the weather or the trail.",
    "There is no shame in starting small and learning well.",
    "A town repays those who take the trouble to know it.",
}

return NPC
