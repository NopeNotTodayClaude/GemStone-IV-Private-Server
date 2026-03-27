-- NPC: Sorvael
-- Role: guard  |  Room: 3727
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guard_amaranth_sorvael"
NPC.name           = "Sorvael"
NPC.article        = ""
NPC.title          = "the gate warden"
NPC.description    = "A tall, seasoned elf in burnished crimson armor with twin golden bands on his vambrace marking twelve years of Legion service.  His posture is a textbook illustration of military bearing."
NPC.home_room_id   = 3727

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
NPC.shift_id       = "amaranth"
NPC.shift_phase    = 0
NPC.spawn_at_start = true

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    hunting = "Fanged rodents south of the gate, nearer the road.  Catacomb entrance is through a hatch off the Shimeraern Var if you're ready for something nastier.",
    gate = "The Amaranth Gate is the oldest of the four.  It has never been breached.  I intend to keep that record.",
    legion = "Twelve years.  I've stood gate duty in rain, ice, and once during a troll siege.  Today is a good day.",
    new = "New to Ta'Vaalor?  Talk to Sassion near the Vermilion Gate.  She finds work for capable people.",
    water = "A glass of water from the Malwith Inn would not be turned away.  Start the errand properly first: QUEST START tv_guard_water_amaranth.",
    work = "Bring water and you'll have done more good than half the volunteers who stop here.",
    dangerous = "Stay on the road south and you'll be fine.  Leave the road and you're on your own.",
    default = "Sorvael gives you a measured look.  'Pass.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Sorvael scans the road south with practiced, unhurried vigilance.",
    "Sorvael adjusts his vambrace without looking down, a habit of years.",
    "Sorvael exchanges a brief nod with a passing Legion patrol.",
    "Sorvael straightens almost imperceptibly as a senior officer passes.",
    "Sorvael rests a hand on his sword pommel, a reflex rather than a threat.",
}
NPC.ambient_chance  = 0.025
NPC.emote_cooldown  = 55
NPC.chat_interval   = 450
NPC.chat_chance     = 0.14
NPC.chat_lines = {
    "Amaranth Gate rewards discipline and exposes the lack of it.",
    "The oldest gate in the city tends to make soldiers straighten their backs.",
    "I've stood this post in sleet, smoke, and worse.  Sunshine is no hardship.",
    "Stay on the road and most of the world remains negotiable.",
    "Newcomers worry about the walls.  Veterans worry about the habits of the people on them.",
    "Merchant traffic has a rhythm to it.  Break that rhythm and I take notice.",
    "A quiet gate is maintained, not granted.",
    "If Sassion sends you on an errand, finish it promptly.  She keeps better records than the quartermaster.",
    "The bridge carries sound cleanly.  I hear impatience long before I see it.",
    "There is honor in holding a line no enemy reaches.",
    "The Legion is built on ordinary days done properly.",
    "I prefer a soldier who asks sensible questions to one who pretends he has none.",
}

return NPC
