-- NPC: Tedrik
-- Role: townsfolk  |  Room: 10424
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "tedrik"
NPC.name           = "Tedrik"
NPC.article        = ""
NPC.title          = "the retired officer"
NPC.description    = "A weathered elven man in his middle centuries, wearing a faded uniform jacket stripped of its rank insignia but clearly maintained with old habits.  He occupies his corner of the tavern with the comfortable permanence of a piece of furniture."
NPC.home_room_id   = 21223   -- LICH 14102009

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
NPC.greeting       = "raises his mug in greeting.  'Sit down.  You've got that look.'"
NPC.dialogues = {
    airship = "Thirteen years as an airship combat officer.  We ran interdiction routes over the Dragonspine.  Different life.",
    combat = "First thing you learn in real combat: nothing goes according to plan.  Second thing: you plan anyway.",
    tactics = "Watch your flanks.  Know your exits before you need them.  Keep something in reserve.  Old advice.  Still works.",
    training = "What are you training?  I can tell you what the Legion looks for, if that helps.  They care about Physical Fitness more than people expect.",
    hunting = "Work up from fanged rodents.  Don't skip the middle.  I've seen adventurers try to skip the middle.  It ends badly.",
    armor = "Get Armor Use ranks before you upgrade your armor.  Sounds obvious.  Nobody does it.",
    catacombs = "I'd wait on the catacombs until you can handle yourself.  Level three, minimum.  Bring herbs.",
    retire = "Retired six years ago.  Miss the airship.  Don't miss the interdiction routes.  Don't miss the paperwork.",
    drink = "Same thing I've been drinking for forty years.  Don't fix what isn't broken.",
    war = "I was posted here during the Undead War resurgence.  Saw the gates close.  Saw them open again.  Prefer the opening.",
    advice = "Stay alive long enough to get good.  That's the whole trick.  Everything else follows.",
    lesson = "If you want the longer lecture, use QUEST START tedrik_lesson and answer like you were paying attention.",
    new = "New here?  Talk to Sassion near the Vermilion Gate for quick silver.  Talk to Thalindra at the Guild for bounties.  And talk to me for free advice.",
    default = "Tedrik wraps both hands around his mug.  'Pull up a chair.  What do you want to know?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Tedrik swirls his drink slowly, staring at nothing in particular.",
    "Tedrik chuckles at something a nearby soldier says and shakes his head.",
    "Tedrik drums two fingers on the table in a short, unconscious pattern.",
    "Tedrik watches the door with the old habit of someone who always notes arrivals.",
    "Tedrik refills his mug from a pitcher, takes a sip, and nods approval.",
    "Tedrik rubs the side of his jaw and gazes toward the window with distant eyes.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 35
NPC.chat_interval   = 450
NPC.chat_chance     = 0.11
NPC.chat_lines = {
    "Most novices think speed saves them.  Usually it's judgment.",
    "A wall, a shield, and a retreat route are all finer friends than pride.",
    "If you leave town unprepared, town gets to see you again too quickly.",
    "The young always want advanced advice first.  The basics are what keep them breathing.",
}

return NPC
