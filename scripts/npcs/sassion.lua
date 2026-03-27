-- NPC: Sassion
-- Role: quest_giver  |  Room: 3490
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "sassion"
NPC.name           = "Sassion"
NPC.article        = ""
NPC.title          = "the errand-keeper"
NPC.description    = "A brisk, practical elven woman with a clipboard and a manner that suggests she has seventeen things to do and your arrival is item eighteen.  She nonetheless makes time for everyone who approaches."
NPC.home_room_id   = 3490

-- ── Capabilities ─────────────────────────────────────────────────────────────
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

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks up from her clipboard with efficient attention.  'What can I do for you?'"
NPC.dialogues = {
    work = "I always have errands that need capable hands.  Ask me about TASKS and I'll tell you what's available.",
    tasks = "Current work: delivery runs to the barracks, item retrieval from the Adventurers Guild, and I need someone to bring a message to the Historical Society.",
    pay = "I pay in silver, promptly, upon completion.  No haggling.  The rate is fair.",
    hunting = "Not hunting work, I'm afraid.  Errands in-city.  But the Adventurers Guild posts combat bounties.",
    new = "New to Ta'Vaalor?  Good.  New people need silver and silver comes from work.  Let's get you started.",
    guild = "Talk to Thalindra at the Adventurers Guild for combat work.  I handle the civilian errands.",
    deliver = "I have a delivery that needs to go to the Amaranth Barracks.  Quick trip, good pay.  Interested?",
    fetch = "I need someone to collect a package from Phisk at the General Exchange and bring it here.  Simple task.",
    message = "Take this message to Archivist Yendrel at the Historical Society and wait for his reply.",
    done = "You've done good work.  Come back when you need more silver.",
    default = "Sassion glances up from her clipboard.  'Looking for work?  You've come to the right person.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Sassion makes a notation on her clipboard and moves briskly to the next item.",
    "Sassion flags down a passing runner and hands them a sealed note.",
    "Sassion scans the street with the evaluating eye of someone assessing potential.",
    "Sassion consults a small schedule book and frowns at it thoughtfully.",
    "Sassion calls out to a passing guardsman, exchanges three words, and nods in satisfaction.",
    "Sassion crosses an item off her list with a decisive stroke.",
}
NPC.ambient_chance  = 0.05
NPC.emote_cooldown  = 25
NPC.chat_interval   = 360
NPC.chat_chance     = 0.17
NPC.chat_lines = {
    "If you want fast silver, I have fast work.",
    "Errands do not complete themselves, despite my regular disappointment on that point.",
    "Reliable hands are harder to find than willing hands.",
    "If you can walk across town and return with the correct package, I can use you.",
    "The city runs on messages, deliveries, and people who show up when expected.",
    "I always have work for someone who listens the first time.",
    "Thalindra handles bounties.  I handle the tasks that keep a city from coming apart.",
    "Do one small job well and I tend to remember your name.",
    "A runner who arrives on time is worth more than three who arrive with excuses.",
    "If you are standing idle, I can improve that condition immediately.",
    "There is always another note to carry, another parcel to fetch, another favor to square away.",
    "People call them little errands until something important fails because no one did them.",
}

return NPC
