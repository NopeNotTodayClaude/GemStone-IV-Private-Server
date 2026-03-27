-- NPC: Daenvith
-- Role: guard  |  Room: 5827
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guard_vermilion_daenvith"
NPC.name           = "Daenvith"
NPC.article        = ""
NPC.title          = "the gate warden"
NPC.description    = "A broad, amiable elven soldier with a cheerful face that somehow doesn't undercut his authority."
NPC.home_room_id   = 5827

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

-- ── Shift system ─────────────────────────────────────────────────────────────
NPC.shift_id       = "vermilion"
NPC.shift_phase    = 1
NPC.spawn_at_start = false

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    cemetery = "Stay on the path if you head out that way.  The cemetery is fine.  What's in it is less fine.",
    gate = "Good post.  Quiet most days.  I prefer busy days, honestly.  Time moves faster.",
    default = "Daenvith nods pleasantly.  'Through you go.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Daenvith hums very quietly under his breath.",
    "Daenvith rocks back slightly on his heels, then corrects to attention.",
    "Daenvith watches a bird land on the gate and seems briefly delighted.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
