-- NPC: Celindra
-- Role: guard  |  Room: 5906
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guard_annatto_celindra"
NPC.name           = "Celindra"
NPC.article        = ""
NPC.title          = "the gate warden"
NPC.description    = "A no-nonsense elven soldier who seems to actively enjoy guard duty, which her colleagues find slightly unsettling."
NPC.home_room_id   = 5906

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
NPC.shift_id       = "annatto"
NPC.shift_phase    = 1
NPC.spawn_at_start = false

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    gate = "Annatto Gate.  I like this post.  Quiet.  You can think.",
    default = "Celindra nods crisply.  'Pass.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Celindra stands in alert, comfortable silence.",
    "Celindra observes a merchant cart with calm attention.",
}
NPC.ambient_chance  = 0.01
NPC.emote_cooldown  = 90

return NPC
