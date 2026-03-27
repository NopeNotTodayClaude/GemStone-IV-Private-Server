-- NPC: an elven citizen
-- Role: townsfolk  |  Room: 3542
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "elven_citizen_walker"
NPC.name           = "an elven citizen"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "A composed elven civilian going about ordinary business with the unhurried ease of someone with somewhere to be but plenty of time to get there."
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
NPC.patrol_rooms   = { 3542, 3519, 3521, 3522, 3542, 3519, 3518, 3542 }
NPC.wander_chance  = 0.3
NPC.move_interval  = 40

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    city = "Ta'Vaalor.  Best city in the Elven Nations.  Don't let anyone from Sylvarraend tell you different.",
    default = "The citizen nods politely and continues on.",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "An elven citizen exchanges a few pleasant words with a neighbor.",
    "An elven citizen pauses to look at goods in a shop window.",
    "An elven citizen nods to a passing guardsman.",
    "An elven citizen adjusts the strap of a market bag and continues walking.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 50

return NPC
