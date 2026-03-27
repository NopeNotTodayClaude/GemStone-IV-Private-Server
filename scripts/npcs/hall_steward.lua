-- NPC: Steward Faelthas
-- Role: service  |  Room: 10330
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "hall_steward"
NPC.name           = "Steward Faelthas"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A dignified elven man who serves as the administrative nerve center of Ta'Vaalor Hall."
NPC.home_room_id   = 10330

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
NPC.greeting       = "rises slightly and inclines his head with formal courtesy."
NPC.dialogues = {
    hall = "Ta'Vaalor Hall handles civic administration for the entire Elven Nations delegation here.",
    meetings = "The conference rooms are bookable for formal occasions.  Inquire at the desk.",
    legion = "Military matters are coordinated through the Hall in conjunction with the barracks commanders.",
    default = "Steward Faelthas inclines his head precisely.  'How may I assist?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Steward Faelthas reviews a document with a critical eye.",
    "Steward Faelthas dispatches a runner with a sealed message.",
    "Steward Faelthas arranges chairs around the conference table with geometric precision.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
