-- NPC: a Legion soldier
-- Role: guard  |  Room: 3489
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "patrol_guard_north"
NPC.name           = "a Legion soldier"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A disciplined elven soldier in the crimson armor of the Vaalor Legion, maintaining order in the northern districts."
NPC.home_room_id   = 3489

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
NPC.patrol_rooms   = { 3489, 3488, 3485, 3486, 3492, 3494, 3495, 3489 }
NPC.wander_chance  = 0.3
NPC.move_interval  = 30

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    legion = "The Vaalor Legion stands ready at all times.",
    court = "The Amaranth Court is the northern heart of the city.",
    default = "The soldier glances at you, then returns to her patrol.",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A Legion soldier marches a crisp patrol route.",
    "A Legion soldier scans the court with alert eyes.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
