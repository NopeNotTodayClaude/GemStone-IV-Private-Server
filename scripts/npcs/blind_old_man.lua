-- NPC: a ragged old man
-- Role: townsfolk  |  Room: 3542
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "blind_old_man"
NPC.name           = "a ragged old man"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A small, ancient-looking man of indeterminate race, sitting against whatever wall is nearest.  His eyes are clouded white, and he taps a worn walking stick on the stones without apparent purpose.  He seems to be listening to something no one else can hear."
NPC.home_room_id   = 3542

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = true
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Wander / patrol ──────────────────────────────────────────────────────────
NPC.patrol_rooms   = { 3542, 3519, 3542 }
NPC.wander_chance  = 0.05
NPC.move_interval  = 120

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    blind = "He cocks his head toward you.  'I see more than most.  Just differently.'",
    prophecy = "He mutters, 'The stone remembers what the water forgets.  Ask the stone.'",
    old = "He chuckles softly.  'Old?  Yes.  I suppose I am.  By most reckonings.'",
    catacombs = "He goes still.  'Old places, those.  Things live there now that don't remember why.'",
    king = "He waves a hand dismissively.  'Kings.  There have been so many kings.'",
    default = "He tilts his head, as if hearing something in your approach.  'Still there?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A ragged old man taps his walking stick against the cobblestones in an irregular rhythm.",
    "A ragged old man cocks his head sharply, listening to something that isn't there.",
    "A ragged old man mutters, 'The east remembers and the west forgets and neither knows what the middle is doing.'",
    "A ragged old man chuckles quietly to himself for no visible reason.",
    "A ragged old man sits in perfect stillness for a long moment, then resumes tapping.",
    "A ragged old man says quietly, 'Something is moving in the dark.  Isn't it always.'",
    "A ragged old man tilts his head toward the sky as if listening to something overhead.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 35

return NPC
