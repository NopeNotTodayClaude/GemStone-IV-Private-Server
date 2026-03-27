-- NPC: Tarneth
-- Role: shopkeeper  |  Room: 10394
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "forge_clerk"
NPC.name           = "Tarneth"
NPC.article        = ""
NPC.title          = "the supply clerk"
NPC.description    = "A stocky elven man with a no-nonsense manner, keeping meticulous inventory of forging materials."
NPC.home_room_id   = 10394

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = true
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Shop ─────────────────────────────────────────────────────────────────────
NPC.shop_id        = 18

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "nods curtly.  'What do you need?'"
NPC.dialogues = {
    supplies = "I stock ores, ingots, and forging tools for smiths.",
    ore = "We carry vaalorn, drakar, imflass, and common metals.  Ask about current availability.",
    forge = "The forge across the way is available for rent by qualified smiths.  Rates by the hour.",
    default = "Tarneth looks up from a ledger.  'Supplies?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Tarneth updates his inventory ledger with efficient strokes.",
    "Tarneth weighs a lump of ore on a scale, noting the result.",
    "Tarneth arranges ingots by type on a heavy wooden shelf.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
