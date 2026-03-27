-- NPC: a road-weary traveler
-- Role: townsfolk  |  Room: 3727
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "traveler_passing"
NPC.name           = "a road-weary traveler"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A dusty traveler in practical traveling clothes, clearly just arrived from somewhere and not entirely sure where to go next."
NPC.home_room_id   = 3727

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
NPC.patrol_rooms   = { 3727, 3483, 3484, 3485, 5826, 3485, 3484, 3483, 3727 }
NPC.wander_chance  = 0.25
NPC.move_interval  = 35

-- ── Rare spawn ───────────────────────────────────────────────────────────────
NPC.rare_spawn     = true
NPC.spawn_chance   = 0.3

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks slightly lost but friendly about it."
NPC.dialogues = {
    travel = "Just arrived from Neartofar.  Three days on the road.  My feet hate me.",
    city = "First time in Ta'Vaalor.  It's bigger than I expected.  And more... serious.",
    neartofar = "Neartofar is pleasant.  Quieter than here.  Different kind of elves.",
    default = "The traveler rubs the back of their neck.  'Still getting my bearings.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A road-weary traveler peers at a posted city notice with tired eyes.",
    "A road-weary traveler sets down a heavy pack and stretches with audible relief.",
    "A road-weary traveler asks a passerby something and gets directions.",
    "A road-weary traveler counts coins carefully before approaching a vendor.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 40

return NPC
