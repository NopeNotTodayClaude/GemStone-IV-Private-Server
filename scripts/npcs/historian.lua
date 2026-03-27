-- NPC: Archivist Yendrel
-- Role: service  |  Room: 10336
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "historian"
NPC.name           = "Archivist Yendrel"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "An ancient-seeming elven scholar buried under stacks of documents.  He speaks slowly but says a great deal."
NPC.home_room_id   = 10336

-- ── Capabilities ─────────────────────────────────────────────────────────────
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

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "peers over an enormous tome.  'History seeker?  You've come to the right place.'"
NPC.dialogues = {
    history = "Ta'Vaalor was founded seven hundred years ago following the first Undead War.  We built here to watch the passes.",
    undead = "The Undead War was a catastrophe.  What walks out there now is a remnant.  A reminder.",
    vaalor = "The Vaalor Elves have maintained this fortress without pause for seven centuries.  We do not forget.",
    legion = "The Legion predates the city by decades.  It was the Legion that chose this site.",
    catacombs = "The catacombs predate the city by centuries.  We know very little about who built them or why.  That concerns me.",
    records = "I maintain records of every significant event in Ta'Vaalor's history.  Ask me anything.",
    default = "Archivist Yendrel looks up with the slow focus of the very learned.  'Ah.  A questioner.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Archivist Yendrel carefully turns the pages of an ancient bound volume.",
    "Archivist Yendrel makes a marginal note in cramped, precise handwriting.",
    "Archivist Yendrel compares two documents side by side, muttering quietly.",
    "Archivist Yendrel blows dust from a newly retrieved scroll and sneezes.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
