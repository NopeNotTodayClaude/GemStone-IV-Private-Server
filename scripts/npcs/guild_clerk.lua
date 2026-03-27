-- NPC: Thalindra
-- Role: service  |  Room: 10331
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guild_clerk"
NPC.name           = "Thalindra"
NPC.article        = ""
NPC.title          = "the guild clerk"
NPC.description    = "A businesslike elven woman who manages the Adventurers' Guild with organized efficiency and barely concealed exasperation."
NPC.home_room_id   = 10331

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = true
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "glances up from behind a stack of contracts.  'Another adventurer.  Lovely.'"
NPC.dialogues = {
    bounties = "I post the active bounty contracts and keep the guild records straight.  Finished contracts, check-ins, and voucher counts all pass through my desk.",
    guild = "The Adventurers' Guild connects capable individuals with those who need capable individuals.",
    register = "Guild registration is free.  You're already eligible simply by being here.",
    bounty = "Pick up a contract, complete it, and report back here or to the taskmaster.  Culls, recoveries, escorts, rescues, and exchanges all go through the ledger now.",
    vouchers = "Swaps cost vouchers.  Keep working and checking in and the guild will keep issuing them.",
    checkin = "Yes, I can record your check-in here.  It keeps your file current.",
    sassion = "Sassion?  She handles the in-city errands.  Find her near the Vermilion Gate.",
    default = "Thalindra looks up.  'Bounty work?  Browse the board.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Thalindra posts a new contract on the bounty board with a decisive pin.",
    "Thalindra crosses a completed bounty off the active list.",
    "Thalindra sorts a pile of contracts by difficulty rating.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60
NPC.chat_interval   = 460
NPC.chat_chance     = 0.08
NPC.chat_lines = {
    "If your contract changed in the field, the ledger still expects you back in one piece.",
    "A neat report closes faster than a dramatic one.",
    "Vouchers are for measured judgment, not indecision.",
}

return NPC
