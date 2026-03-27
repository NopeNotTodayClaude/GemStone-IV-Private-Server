-- NPC: a Vaalor guardsman
-- Role: guard  |  Room: 3504
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "patrol_guard_west"
NPC.name           = "a Vaalor guardsman"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An elven guard in Legion armor patrolling the western residential streets."
NPC.home_room_id   = 3504

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
NPC.patrol_rooms   = { 3504, 3507, 3508, 3509, 3510, 3511, 3504 }
NPC.wander_chance  = 0.3
NPC.move_interval  = 30

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    default = "The guardsman gives you a nod and continues his rounds.",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A Vaalor guardsman checks that a shop door is properly closed.",
    "A Vaalor guardsman nods to a passing citizen.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 70

return NPC
