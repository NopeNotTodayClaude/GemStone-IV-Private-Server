-- NPC: a Vaalor guardsman
-- Role: guard  |  Room: 3542
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "patrol_guard_south"
NPC.name           = "a Vaalor guardsman"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An elven guard in polished crimson and gold armor, patrolling the southern streets of Ta'Vaalor with purpose."
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
NPC.patrol_rooms   = { 3542, 3519, 3518, 3521, 3522, 3523, 5906, 3523, 3522, 3542 }
NPC.wander_chance  = 0.35
NPC.move_interval  = 30

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    trouble = "Keep the peace and there'll be no trouble from me.",
    city = "Ta'Vaalor is the jewel of the Elven Nations.  Treat it with respect.",
    hunting = "Hunting is outside the walls.  Inside, you keep your weapons sheathed.",
    default = "The guardsman nods but keeps walking.",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A Vaalor guardsman marches past with measured strides.",
    "A Vaalor guardsman surveys the area with a watchful eye.",
    "A Vaalor guardsman adjusts his grip on his spear.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
