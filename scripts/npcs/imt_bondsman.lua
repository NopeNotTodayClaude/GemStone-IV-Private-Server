-- NPC: Icemule Trace Bondsman
local NPC = {}

NPC.template_id    = "imt_bondsman"
NPC.name           = "the bondsman"
NPC.article        = ""
NPC.title          = "of Clovertooth Hall"
NPC.description    = "A flinty-faced halfling sits behind a narrow desk with all the warmth of a frozen coin.  His expression suggests he expects to be disappointed and intends to charge for it."
NPC.home_room_id   = 2438   -- LICH 4043042

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

NPC.greeting       = "eyes you suspiciously.  'If you're here to waste my time, take a number and waste it efficiently.'"
NPC.dialogues = {
    work = "I hand out messages.  You carry them.  The world keeps turning.  If that sounds manageable, look through my available work.",
    jobs = "Mostly notes, packets, and reminders for people too important to walk a street themselves.",
    debt = "Pay what you owe and you'll hear my voice less often.  That's a service to both of us.",
    hall = "Clovertooth Hall runs on signatures, seals, and people who can read directions.",
    default = "The bondsman peers over his desk.  'Speak up.'",
}
NPC.ambient_emotes = {
    "The bondsman aligns three stacks of paperwork until their edges match perfectly.",
    "The bondsman checks a figure twice, then glares as though the number offended him personally.",
    "The bondsman reaches for a fresh form with grim resignation.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45
NPC.chat_interval  = 430
NPC.chat_chance    = 0.11
NPC.chat_lines = {
    "If I trusted people to remember things, I'd be out of a profession.",
    "One delivered packet saves me six complaints.",
    "Promptness is cheaper than apology.",
    "The cold preserves a great many things.  Sadly, not competence.",
}

return NPC
