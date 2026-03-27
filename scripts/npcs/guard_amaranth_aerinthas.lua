-- NPC: Aerinthas
-- Role: guard  |  Room: 3727
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guard_amaranth_aerinthas"
NPC.name           = "Aerinthas"
NPC.article        = ""
NPC.title          = "the gate warden"
NPC.description    = "A younger elven soldier with eager eyes and the slightly over-polished armor of someone still new enough to care deeply about appearances."
NPC.home_room_id   = 3727

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
NPC.shift_id       = "amaranth"
NPC.shift_phase    = 1
NPC.spawn_at_start = false

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    hunting = "I'm still learning the creature patterns.  Sorvael says stay on the road south.  I'd listen to him.",
    gate = "It's an honor to stand this post.  I mean that.",
    legion = "Third year of service.  Gate duty is serious work.  Some don't understand that.",
    default = "Aerinthas stands straight.  'State your business.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Aerinthas stands in precisely perfect attention.",
    "Aerinthas watches a merchant cart pass through with careful eyes.",
    "Aerinthas shifts his grip on his spear, then corrects himself back to regulation hold.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
