-- NPC: a prosperous-looking elven merchant
-- Role: townsfolk  |  Room: 3542
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "elven_merchant_court"
NPC.name           = "a prosperous-looking elven merchant"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A well-dressed elf with a merchant's eye for opportunity and the rings to prove past success.  He seems to be between meetings, conducting one side of a negotiation in his head."
NPC.home_room_id   = 3542

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
NPC.greeting       = "glances up from his mental calculations."
NPC.dialogues = {
    trade = "Imports from Neartofar, exports northward.  The circuit works if you know the timing.",
    prices = "Everything has a price.  Knowing what that price is before your counterpart does - that's the art.",
    legion = "Good for business, a stable Legion.  People shop when they feel safe.",
    default = "The merchant looks up briefly.  'Mm?  Oh.  Not currently buying, if that's what you're asking.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A prosperous-looking elven merchant counts something on his fingers and nods.",
    "A prosperous-looking elven merchant reviews a small ledger with practiced speed.",
    "A prosperous-looking elven merchant watches a trade carriage pass with professional interest.",
    "A prosperous-looking elven merchant exchanges brief words with a passing courier.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
