-- NPC: an elven woman with a young child
-- Role: townsfolk  |  Room: 3542
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "elven_mother_child"
NPC.name           = "an elven woman with a young child"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "A graceful elven woman holding the hand of a small child who is clearly doing everything possible to be anywhere else."
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
NPC.patrol_rooms   = { 3542, 3519, 3542 }
NPC.wander_chance  = 0.15
NPC.move_interval  = 60

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    child = "She smiles apologetically.  'He finds the fountain more interesting than anything I'm trying to show him.'",
    default = "She nods pleasantly while keeping hold of the child's hand.",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "An elven woman with a young child guides the child away from the edge of the fountain for the third time.",
    "An elven woman with a young child answers a string of questions patiently.",
    "An elven woman with a young child accepts a pastry from a vendor and hands it to the child.",
    "An elven woman with a young child watches the child wave enthusiastically at a passing soldier.",
    "An elven woman with a young child crouches to point out something in the stonework.",
}
NPC.ambient_chance  = 0.05
NPC.emote_cooldown  = 30

return NPC
