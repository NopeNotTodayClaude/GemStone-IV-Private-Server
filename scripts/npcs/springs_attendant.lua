-- NPC: Vaelindra
-- Role: townsfolk  |  Room: 10343
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "springs_attendant"
NPC.name           = "Vaelindra"
NPC.article        = ""
NPC.title          = "the bath attendant"
NPC.description    = "A serene elven woman in crisp white linen, who manages the mineral springs with quiet efficiency."
NPC.home_room_id   = 10343

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
NPC.greeting       = "smiles and gestures toward the steaming pools."
NPC.dialogues = {
    springs = "The mineral waters here are reputed to have restorative properties.  They do.",
    bath = "A soak in the springs refreshes both body and spirit after a long campaign.",
    cost = "Use of the springs is free to citizens and visiting adventurers alike.",
    default = "Vaelindra smiles peacefully.  'Would you like to use the springs?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Vaelindra replenishes a tray of fresh towels near the springs.",
    "Vaelindra tests the temperature of the water with her hand and nods.",
    "Vaelindra arranges small vials of aromatic oils beside the bathing area.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
