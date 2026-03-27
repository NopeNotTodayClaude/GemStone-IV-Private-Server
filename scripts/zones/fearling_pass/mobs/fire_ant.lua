-- Creature: fire ant
-- Zone: Fearling Pass / Barefoot Hill  |  Level: 1
local Creature = {}

Creature.id              = 9001
Creature.name            = "fire ant"
Creature.level           = 1
Creature.family          = "insect"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 30
Creature.hp_variance     = 4

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 22
Creature.ds_bolt         = 10
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 22, damage_type = "puncture" },
    { type = "sting", as = 18, damage_type = "puncture" },
}

Creature.spells = {}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "fire_ant_acid_sting",
}

Creature.immune = {
    "fire",
}

Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a fire ant mandible"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
Creature.spawn_rooms = {
    6090,
    6091,
    6092,
    6093,
    6094,
    6095,
    6096,
    6097,
    6098,
    6099,
    6100,
    10269,
    10290,
    10291,
    10292,
    10295,
    10296,
    10297
}

Creature.roam_rooms = {
    6090,
    6091,
    6092,
    6093,
    6094,
    6095,
    6096,
    6097,
    6098,
    6099,
    6100,
    10269,
    10290,
    10291,
    10292,
    10295,
    10296,
    10297
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 150
Creature.max_count       = 3

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "This worker fire ant is roughly twice the size of its mundane kin.  Its burnt-orange carapace gleams dully in whatever light reaches it, and its mandibles click with a dry, ominous sound.  The stinger at the tip of its segmented abdomen is swollen and clearly capable of delivering a nasty dose of venom."

return Creature
