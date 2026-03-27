-- NPC: a light-robed erithian woman
-- Role: townsfolk  |  Room: 3542
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "erithian_woman"
NPC.name           = "a light-robed erithian woman"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A slender erithian woman in pale grey robes that seem too light for the season.  She moves through the city with deliberate calm, watching everything with large amber eyes that seem to catalog what they see."
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
NPC.patrol_rooms   = { 3542, 3521, 3523, 5906, 3523, 3522, 3542, 3519, 3518, 3542 }
NPC.wander_chance  = 0.15
NPC.move_interval  = 60

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    erithian = "She regards you quietly.  'We are a long way from home, you and I both.'",
    watching = "She tilts her head.  'There is much to observe.  I find it useful.'",
    city = "She considers the question.  'It is very... purposeful.  The elves here have much intention.'",
    default = "She meets your eyes for a moment, offers a slight smile, and says nothing.",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A light-robed erithian woman watches the street traffic with calm, careful attention.",
    "A light-robed erithian woman pauses to examine the stonework of a building, touching it briefly.",
    "A light-robed erithian woman makes a small mark in a slim journal, then continues walking.",
    "A light-robed erithian woman tilts her head at something only she notices.",
    "A light-robed erithian woman stands very still for a moment, eyes half-closed, then resumes.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 60

return NPC
