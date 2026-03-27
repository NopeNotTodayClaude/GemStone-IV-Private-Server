-- Creature: plains lion
-- Zone: Grasslands / Foothills & Grassland  |  Level: 18
local Creature = {}

Creature.id              = 9007
Creature.name            = "plains lion"
Creature.level           = 18
Creature.family          = "feline"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 222
Creature.hp_variance     = 16

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 168
Creature.ds_bolt         = 78
Creature.td_spiritual    = 57
Creature.td_elemental    = 57
Creature.udf             = 8
Creature.armor_asg       = 3
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 202, damage_type = "slash" },
    { type = "bite", as = 196, damage_type = "puncture" },
    { type = "pounce", as = 192, damage_type = "crush" },
}

Creature.spells = {}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "pounce_maneuver",
    "hamstring",
}

Creature.immune = {}

Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a plains lion pelt"
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

Creature.roam_chance     = 25
Creature.respawn_seconds = 360
Creature.max_count       = 5

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "A tawny-golden coat stretched over two hundred pounds of hunting muscle, the plains lion surveys its domain from a low rise, tail lashing with slow patience.  The mane of the male is a darker ochre, almost russet around the face.  It seems aware of its own power and in no particular hurry to demonstrate it."

return Creature
