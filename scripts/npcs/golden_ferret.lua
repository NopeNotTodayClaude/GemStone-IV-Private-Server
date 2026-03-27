-- NPC: a sleek golden ferret
-- Role: townsfolk  |  Room: 3542
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "golden_ferret"
NPC.name           = "a sleek golden ferret"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A remarkably beautiful ferret with lustrous golden fur and bright, intelligent eyes.  It moves with the fluid confidence of an animal that knows it belongs wherever it happens to be."
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
NPC.patrol_rooms   = { 3542, 3519, 3498, 3497, 3496, 3488, 3485, 3498, 3500, 3502, 3508, 3507, 3504, 3519, 3521, 3522, 3523, 3542, 3544, 3542 }
NPC.wander_chance  = 0.6
NPC.move_interval  = 15

NPC.unkillable     = true

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    default = "The ferret fixes you with a bright, evaluating stare, then moves on.",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A sleek golden ferret darts between someone's legs without breaking stride.",
    "A sleek golden ferret stands on its hind legs, peering at something shiny with intense interest.",
    "A sleek golden ferret snatches a dropped coin and is gone before anyone can react.",
    "A sleek golden ferret investigates a crack in the cobblestones with its nose.",
    "A sleek golden ferret flows over a barrel like water and disappears behind it.",
    "A sleek golden ferret emerges from somewhere improbable, shakes itself, and moves on.",
    "A sleek golden ferret sits up and stares at you directly for an unsettling moment, then loses interest.",
}
NPC.ambient_chance  = 0.08
NPC.emote_cooldown  = 15

return NPC
