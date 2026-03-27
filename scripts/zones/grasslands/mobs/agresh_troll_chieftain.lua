-- Creature: Agresh troll chieftain
-- Zone: Grasslands / Foothills  |  Level: 20
local Creature = {}

Creature.id              = 9008
Creature.name            = "Agresh troll chieftain"
Creature.level           = 20
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 245
Creature.hp_variance     = 18

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 161
Creature.ds_bolt         = 80
Creature.td_spiritual    = 63
Creature.td_elemental    = 63
Creature.udf             = 0
Creature.armor_asg       = 12
Creature.armor_natural   = false

Creature.attacks = {
    { type = "warhammer", as = 215, damage_type = "crush" },
    { type = "claw", as = 208, damage_type = "slash" },
    { type = "pound", as = 200, damage_type = "crush" },
}

Creature.spells = {
    { name = "gesture_battle_cry", cs = 88, as = 0 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "troll_regeneration",
    "chieftain_war_cry",
    "rally_trolls",
}

Creature.immune = {}

Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a troll chieftain war-trophy"
Creature.special_loot = {
    "a crude tribal fetish",
}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
Creature.spawn_rooms = {
    10171,
    10172,
    10173,
    10174,
    10175,
    10176,
    10177,
    10178,
    10179,
    10180,
    10181,
    10182,
    10185,
    10186,
    10187,
    10188,
    10183,
    10184,
    10189,
    10190,
    10191,
    10192,
    10193,
    10194
}

Creature.roam_rooms = {
    10171,
    10172,
    10173,
    10174,
    10175,
    10176,
    10177,
    10178,
    10179,
    10180,
    10181,
    10182,
    10185,
    10186,
    10187,
    10188,
    10183,
    10184,
    10189,
    10190,
    10191,
    10192,
    10193,
    10194,
    10195,
    10196,
    10197,
    10198,
    10199,
    10200,
    10201,
    10202,
    10203,
    10204,
    10205,
    10206,
    10207
}

Creature.roam_chance     = 10
Creature.respawn_seconds = 480
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Taller than its subordinates and marked by war-paint smeared across its face and chest, the Agresh troll chieftain radiates a brutal authority.  Battle trophies hang from a broad leather harness, and a massive warhammer rests across one shoulder with casual menace.  The tribal tattoos covering its arms mark a lifetime of victories."

return Creature
