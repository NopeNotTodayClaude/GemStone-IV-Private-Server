-- NPC: Raertria
-- Role: guard  |  Room: 5827
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guard_vermilion_raertria"
NPC.name           = "Raertria"
NPC.article        = ""
NPC.title          = "the gate warden"
NPC.description    = "A sharp-featured elven woman whose ice-grey eyes miss nothing.  Her armor shows deliberate care and the faint marks of past combat.  She watches every person who passes through her gate."
NPC.home_room_id   = 5827

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
NPC.shift_id       = "vermilion"
NPC.shift_phase    = 0
NPC.spawn_at_start = true

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    cemetery = "The Vermilion Gate leads to the cemetery road.  There are things out there that don't respect the dead.  Be armed.",
    undead = "I've put down things that should have stayed buried.  This gate is the line.",
    gate = "Nothing passes through here that I don't account for.  Nothing.",
    heritage = "The Vaalor have guarded this gate for seven centuries.  I don't plan to be the weak link.",
    new = "Talk to Sassion if you want paying work.  She's near the barracks, east of here.",
    water = "If you've a mind to help, fetch me a glass of water from Malwith Inn.  Use QUEST START tv_guard_water_vermilion and don't dawdle.",
    work = "Bring me water and you'll have earned your silver honestly.",
    default = "Raertria studies you with cool grey eyes.  'Purpose?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Raertria surveys the road beyond the gate with the steady intensity of someone expecting trouble.",
    "Raertria checks the gate mechanism without interrupting her watch.",
    "Raertria narrows her eyes at a passing traveler, then lets them through.",
    "Raertria shifts her spear to her other hand in a smooth, practiced motion.",
    "Raertria exchanges a quiet word with a Legion patrol heading out.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 50
NPC.chat_interval   = 450
NPC.chat_chance     = 0.14
NPC.chat_lines = {
    "Vermilion Gate stays honest because the dead beyond it do not negotiate.",
    "If you walk cemetery road, walk it armed and awake.",
    "Half my work is watching who pretends not to be nervous.",
    "Nothing passes this gate uncounted.",
    "The road outside teaches respect very quickly.",
    "I trust a calm traveler more than a cheerful one.",
    "Sassion has a better eye for useful newcomers than most officers I have known.",
    "This post is quiet until it is not.  That is why it remains guarded.",
    "Some people hear cemetery bells in the wind whether they are there or not.",
    "I would rather answer ten questions than scrape one fool off the road.",
    "Gate duty is not glamorous.  It is merely essential.",
    "If you come back looking pale, I will assume you ignored instructions.",
}

return NPC
