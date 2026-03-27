-- NPC: an elven student
-- Zone/Town: auto-placed  |  Room: 5907
local NPC = {}

NPC.template_id    = "tv_elven_student"
NPC.name           = "an elven student"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "A young elven student with a stack of books tucked under one arm."
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
    books = "These are military histories.  Dry reading, according to everyone who has not opened them.",
    gate = "Victory Gate is a better place to observe people than the library, though less comfortable.",
    history = "Ta'Vaalor remembers its wars in stone, ritual, and lecture alike.",
    study = "I am meant to be comparing campaign journals.  Instead I am people-watching.",
    default = "The student shifts the books in his arms.  'If this is about strategy, I may have opinions.'",
}
NPC.ambient_emotes = {
    "The student flips a page with his thumb and frowns in concentration.",
    "The student glances from the page to the gate traffic, clearly comparing theory to reality.",
    "The student murmurs a date to himself and scratches a note in the margin of a text.",
    "The student shifts his stack of books and nearly loses one before catching it neatly.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 75

return NPC
