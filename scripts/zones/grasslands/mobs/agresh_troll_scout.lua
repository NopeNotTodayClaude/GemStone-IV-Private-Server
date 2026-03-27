-- Creature: Agresh troll scout
-- Zone: Grasslands / Barley Field  |  Level: 14
local Creature = {}

Creature.id              = 9002
Creature.name            = "Agresh troll scout"
Creature.level           = 14
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 178
Creature.hp_variance     = 14

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 131
Creature.ds_bolt         = 62
Creature.td_spiritual    = 46
Creature.td_elemental    = 46
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false

Creature.attacks = {
    { type = "handaxe", as = 175, damage_type = "slash" },
    { type = "dagger", as = 168, damage_type = "puncture" },
}

Creature.spells = {}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "troll_regeneration",
    "scouting_awareness",
}

Creature.immune = {}

Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a troll scalp"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
Creature.spawn_rooms = {
    10208,
    10209,
    10210,
    10211,
    10212,
    10213,
    10214,
    10215,
    10233,
    10234,
    10235,
    10236,
    10237,
    10238,
    10239,
    10261
}

Creature.roam_rooms = {
    10208,
    10209,
    10210,
    10211,
    10212,
    10213,
    10214,
    10215,
    10233,
    10234,
    10235,
    10236,
    10237,
    10238,
    10239,
    10261,
    10216,
    10217,
    10218,
    10219
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 320
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Lean and quick for its kind, the Agresh troll scout moves with a purposeful, loping gait.  It wears a tattered leather jerkin and carries a pair of crude weapons, scanning its territory with small, mean eyes that miss very little."

return Creature
