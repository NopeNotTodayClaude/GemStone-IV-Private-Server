-- NPC: Auviendal
-- Role: service  |  Room: 10324
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "bank_teller"
NPC.name           = "Auviendal"
NPC.article        = ""
NPC.title          = "the bank teller"
NPC.description    = "A composed elven woman who handles large sums of silver with the calm detachment of someone who has counted beyond caring."
NPC.home_room_id   = 10324

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
NPC.greeting       = "looks up from a ledger with composed attention."
NPC.dialogues = {
    deposit = "DEPOSIT to add silver to your account.  WITHDRAW to take it out.",
    account = "Your account is secure.  The Bank of Ta'Vaalor has operated continuously for four centuries.",
    exchange = "We handle currency exchange.  Ask about current rates.",
    interest = "We do not pay interest.  We provide security.  That is the service.",
    default = "Auviendal folds her hands.  'How can I assist you?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Auviendal counts a stack of coins with rapid, practiced flicks.",
    "Auviendal records a transaction in a large leather-bound ledger.",
    "Auviendal validates a document with a wax seal.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
