-- NPC: a white-robed acolyte
-- Role: townsfolk  |  Room: 3535
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "lorminstra_acolyte"
NPC.name           = "a white-robed acolyte"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A young elven man in the white robes of a religious novice, carrying a stack of prayer texts.  He looks earnest and slightly overwhelmed by everything."
NPC.home_room_id   = 3535

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
NPC.patrol_rooms   = { 3535, 3539, 3542, 3519, 3535 }
NPC.wander_chance  = 0.2
NPC.move_interval  = 55

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "nearly drops his stack of texts, then recovers.  'Ah - good day!'"
NPC.dialogues = {
    faith = "I'm still learning.  The priestess says understanding comes with time.  And practice.",
    lorminstra = "I joined the clergy last year.  There is more to it than I expected.  In a good way, mostly.",
    prayer = "I'm practicing the blessing forms.  I can do the basic ones reliably now.",
    default = "The acolyte looks up from his texts, slightly flustered.  'Oh!  Hello.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A white-robed acolyte studies a page of text with furrowed concentration.",
    "A white-robed acolyte fumbles his prayer book, catches it, and looks around to see if anyone noticed.",
    "A white-robed acolyte copies something from one text to another, tongue slightly out.",
    "A white-robed acolyte asks a passing citizen a question, listens intently, and thanks them.",
    "A white-robed acolyte pauses, closes his eyes as if recalling something, then nods.",
}
NPC.ambient_chance  = 0.05
NPC.emote_cooldown  = 30

return NPC
