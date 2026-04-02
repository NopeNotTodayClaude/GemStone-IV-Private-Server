-- NPC: Caerindra
-- Role: service  |  Room: 10302
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "travel_clerk"
NPC.name           = "Caerindra"
NPC.article        = ""
NPC.title          = "the travel clerk"
NPC.description    = "An efficient elven woman with a desk buried under maps, manifests, and scheduling documents."
NPC.home_room_id   = 10302

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
NPC.greeting       = "looks up from a sheaf of papers and produces a professional smile."
NPC.dialogues = {
    travel = "I handle travel arrangements, airship bookings, and route information.",
    airship = "The airship runs on a schedule.  Ask about current destinations and fares.",
    routes = "I have maps of the major trade routes if you need them.",
    neartofar = "Neartofar is our closest neighbor.  The road south from the Annatto Gate.",
    default = "Caerindra looks up from a map.  'Traveling somewhere?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Caerindra updates a schedule board behind her desk.",
    "Caerindra rolls a map carefully and tucks it into a labeled cylinder.",
    "Caerindra consults a thick ledger of departure times.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

TravelOfficeNPC.attach(NPC, "tv_travel")

return NPC
