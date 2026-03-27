-- NPC: a robed erithian monk
-- Role: townsfolk  |  Room: 3539
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "erithian_monk"
NPC.name           = "a robed erithian monk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A serene erithian man in flowing slate-grey robes bound at the waist with a simple cord.  Every movement he makes is deliberate and unhurried, as if he has personally exempted himself from the concept of rush."
NPC.home_room_id   = 3539

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
NPC.patrol_rooms   = { 3539, 3540, 3535, 3539 }
NPC.wander_chance  = 0.12
NPC.move_interval  = 75

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    monk = "He bows slightly.  'We follow the path of contemplation.  There is much to contemplate here.'",
    meditation = "He pauses.  'Stillness is not emptiness.  It is attention without attachment.'",
    arkati = "He inclines his head.  'All worthy of respect.  The path simply differs.'",
    erithian = "He smiles faintly.  'We come from far away.  The distance teaches patience.'",
    default = "He bows his head slowly and says nothing, which manages to feel like a complete answer.",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A robed erithian monk stands completely motionless, eyes half-closed.",
    "A robed erithian monk bows slightly to a passing stranger, who looks startled.",
    "A robed erithian monk traces a slow, precise gesture with one hand, then lowers it.",
    "A robed erithian monk examines a small stone he is carrying with quiet attention.",
    "A robed erithian monk sits cross-legged on the ground with perfect composure.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 55

return NPC
