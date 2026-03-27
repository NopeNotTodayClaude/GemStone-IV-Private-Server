-- NPC: Captain Irinthal
-- Role: guard  |  Room: 3542
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guard_captain_irinthal"
NPC.name           = "Captain Irinthal"
NPC.article        = ""
NPC.title          = "of the Vaalor Legion"
NPC.description    = "A commanding elven officer in full ceremonial plate bearing the crest of the Captain's rank - a golden eagle clutching a spear.  His face is all sharp angles and authority.  Soldiers visibly improve their posture when he approaches."
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
NPC.patrol_rooms   = { 3542, 3519, 3518, 3516, 3509, 3507, 3504, 3498, 3500, 3502, 3508, 3510, 3511, 3512, 3513, 3526, 3529, 3530, 3531, 3532, 3533, 3534, 3535, 3539, 3540, 3537, 3536, 3524, 3525, 3522, 3523, 3542 }
NPC.wander_chance  = 1.0
NPC.move_interval  = 45

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    trouble = "Report any disturbance directly to me or to the nearest guardsman.  We respond quickly.",
    law = "The laws of Ta'Vaalor are not suggestions.  Violations are dealt with promptly.",
    legion = "The Legion maintains peace so that citizens and visitors alike may go about their lives safely.  That is the job.",
    hunting = "Keep your hunts outside the city walls.  The gates exist for a reason.",
    king = "King Qalinor's word is law.  I enforce it.  That's the extent of my philosophy.",
    patrol = "I walk every street in this city.  Every one.  I know them all.",
    new = "New to the city?  The Adventurers' Guild posts work.  Sassion near the Vermilion Gate is another resource.",
    default = "Captain Irinthal fixes you with a level, assessing look.  'Is there a problem?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Captain Irinthal nods curtly to a passing guardsman, who visibly straightens.",
    "Captain Irinthal pauses to scan the street in both directions before continuing.",
    "Captain Irinthal exchanges a quiet word with a Legion patrol, who snap to attention.",
    "Captain Irinthal makes a mental note of something he's observed, his expression unreadable.",
    "Captain Irinthal adjusts the drape of his cape in a small, precise gesture.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 50

return NPC
