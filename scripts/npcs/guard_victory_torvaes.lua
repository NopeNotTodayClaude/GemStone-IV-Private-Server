-- NPC: Torvaes
-- Role: guard  |  Room: 5907
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guard_victory_torvaes"
NPC.name           = "Torvaes"
NPC.article        = ""
NPC.title          = "the gate warden"
NPC.description    = "A steady, methodical elven soldier who takes notes in a small journal between travelers, recording traffic patterns with quiet diligence."
NPC.home_room_id   = 5907

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = true
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Shift system ─────────────────────────────────────────────────────────────
NPC.shift_id       = "victory"
NPC.shift_phase    = 1
NPC.spawn_at_start = false

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    notes = "I track traffic patterns.  Academically interesting.  Laerindra says I'm strange.  She's not wrong.",
    gate = "Victory Gate.  Trade and hunter traffic primarily.  Steady throughput.",
    default = "Torvaes makes a quick note and looks up.  'Pass.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Torvaes makes a notation in a small leather journal.",
    "Torvaes counts a group of travelers passing through with quiet murmured numbers.",
    "Torvaes stands watch with calm, analytical attention.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60
NPC.chat_interval   = 480
NPC.chat_chance     = 0.13
NPC.chat_lines = {
    "Seven wagons, nine hunters, two couriers, and one liar before noon.  A balanced morning.",
    "You can measure a city by what comes through its gates.  Ta'Vaalor measures well.",
    "Traffic slows whenever rain threatens, even if the rain never arrives.",
    "People think I count for the ledger.  Mostly I count because patterns matter.",
    "Laerindra says my notes will outlive me.  I hope so.",
    "Trade caravans favor this route when the southern weather behaves itself.",
    "The bridge sounds different under soldiers than it does under merchants.",
    "I once guessed a traveler's origin from his boots alone.  I was nearly correct.",
    "Victory Gate gets more farmers in spring and more bragging in autumn.",
    "Quiet roads mean either peace or trouble thinking very carefully.",
    "A gate journal is less glamorous than a sword, but it lasts longer.",
    "If the numbers change, I like to know why.",
}

return NPC
