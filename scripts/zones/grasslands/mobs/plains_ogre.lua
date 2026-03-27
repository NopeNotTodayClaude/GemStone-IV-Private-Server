-- Creature: plains ogre
-- Zone: Grasslands / Foothills  |  Level: 17
local Creature = {}

Creature.id              = 9006
Creature.name            = "plains ogre"
Creature.level           = 17
Creature.family          = "ogre"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 212
Creature.hp_variance     = 16

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 145
Creature.ds_bolt         = 70
Creature.td_spiritual    = 54
Creature.td_elemental    = 54
Creature.udf             = 0
Creature.armor_asg       = 9
Creature.armor_natural   = false

Creature.attacks = {
    { type = "mace", as = 196, damage_type = "crush" },
    { type = "fist", as = 188, damage_type = "crush" },
}

Creature.spells = {}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "sunder_shield",
    "powerful_blow",
}

Creature.immune = {}

Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "an ogre tusk"
Creature.special_loot = {}

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

Creature.roam_chance     = 15
Creature.respawn_seconds = 360
Creature.max_count       = 5

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Towering a full head above even tall giantmen, the plains ogre is a broad-shouldered brute that moves with surprising speed for its bulk.  Dull eyes peer out from beneath a heavy brow, and a jutting lower jaw pushes a pair of short tusks outward.  It carries a heavy mace in one fist as though it weighed nothing."

return Creature
