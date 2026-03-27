-- NPC: Magistrate Seldren
-- Role: service  |  Room: 10382
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "justice_clerk"
NPC.name           = "Magistrate Seldren"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A severe elven magistrate with a wig that adds authority to an already imposing presence."
NPC.home_room_id   = 10382

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
NPC.greeting       = "observes your approach with judicial attention."
NPC.dialogues = {
    law = "The laws of Ta'Vaalor are clear.  Ignorance is not a defense.",
    fines = "Outstanding violations must be cleared before the court will hear other matters.",
    justice = "Justice in Ta'Vaalor is swift and impartial.  Usually.",
    default = "Magistrate Seldren fixes you with a judicial stare.  'Yes?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Magistrate Seldren reviews a case file with a disapproving expression.",
    "Magistrate Seldren makes a ruling notation in a bound court record.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 75

return NPC
