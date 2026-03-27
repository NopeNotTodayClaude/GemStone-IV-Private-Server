-- NPC: Registrar Sorvian
-- Role: service  |  Room: 10313
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "wyvern_registrar"
NPC.name           = "Registrar Sorvian"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A fastidious elven bureaucrat with immaculate robes and an expression of pained tolerance for the chaos of the living."
NPC.home_room_id   = 10313

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
NPC.greeting       = "adjusts his spectacles and produces a blank form with practiced efficiency."
NPC.dialogues = {
    register = "I handle citizenship registration, deed sales, property records, and surname registration.",
    citizenship = "To register as a citizen requires proof of residence and a modest filing fee.",
    surname = "Surname registration is a formal process.  The name must not be taken and must meet standards of propriety.",
    deeds = "Property deed records are maintained here.  All sales must be filed within thirty days.",
    default = "Registrar Sorvian peers over his spectacles.  'Paperwork?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Registrar Sorvian stamps a document with finality.",
    "Registrar Sorvian files papers into a floor-to-ceiling cabinet with geometric precision.",
    "Registrar Sorvian reads a document, occasionally making tiny corrections.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
