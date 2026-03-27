-- NPC: Wehnimer's Landing Town Clerk
local NPC = {}

NPC.template_id    = "wl_town_clerk"
NPC.name           = "the town clerk"
NPC.article        = ""
NPC.title          = "of Moot Hall"
NPC.description    = "A tired but efficient clerk presides over a hill of ledgers, notes, and stamped forms with the practiced misery of a civil servant who has seen everything twice."
NPC.home_room_id   = 7970   -- LICH 2020

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

NPC.greeting       = "glances up from a ledger.  'If you're here to settle your debt, get in line.  If you're here to work, speak clearly.'"
NPC.dialogues = {
    work = "I do, on occasion, require reliable legs and a basic respect for sealed documents.  Use QUESTS and take one of my dispatches if you're not above honest work.",
    jobs = "Merchants never stop sending complaints, requests, and invoices.  I never stop needing runners.",
    debt = "Everyone wants to complain about debt until it's time to pay it.",
    runner = "The runners think I enjoy this paperwork.  I enjoy it more when someone else carries part of it across town.",
    default = "The town clerk squints down at his paperwork.  'Well?  Debt, registry, or work?'",
}
NPC.ambient_emotes = {
    "The town clerk thumps a stack of papers square and reaches for another form.",
    "The town clerk stamps a document with unnecessary force.",
    "The town clerk mutters under his breath while balancing two ledgers at once.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45
NPC.chat_interval  = 420
NPC.chat_chance    = 0.12
NPC.chat_lines = {
    "There is always another dispatch.",
    "If people filed on time, I'd die of shock within the hour.",
    "Reliable runners are worth their weight in vellum.",
    "A closed ledger is a beautiful thing.",
}

return NPC
