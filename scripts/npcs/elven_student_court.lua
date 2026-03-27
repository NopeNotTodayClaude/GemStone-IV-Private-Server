-- NPC: a young elven student
-- Role: townsfolk  |  Room: 3542
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "elven_student_court"
NPC.name           = "a young elven student"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A teenage elf with ink-stained fingers and the wide-eyed intensity of someone who has recently discovered that the world is larger than expected."
NPC.home_room_id   = 3542

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

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "immediately looks up from his scroll with excited attention."
NPC.dialogues = {
    training = "I'm studying at the Historical Society.  Are you an adventurer?  What level?  What do you train?",
    history = "Archivist Yendrel says the city used to be twice this size before the second Undead War.  Fascinating.",
    monsters = "I've been reading about fanged rodents.  Are they actually intelligent?  The texts are unclear.",
    magic = "I'm trying to decide between clerical magic and elemental.  Do you have a recommendation?",
    default = "The student looks up eagerly.  'Oh!  Are you an adventurer?  Can I ask you some questions?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A young elven student copies something from a posted notice into a notebook.",
    "A young elven student reads a scroll with his lips slightly moving.",
    "A young elven student looks up sharply at a passing group of armed adventurers.",
    "A young elven student taps his quill on his notebook, thinking hard.",
    "A young elven student waves to someone across the court with unbounded enthusiasm.",
}
NPC.ambient_chance  = 0.06
NPC.emote_cooldown  = 25

return NPC
