-- Creature: thyril
-- Zone: Icemule Trace / Snowflake Vale Clearings  |  Level: 2
local Creature = {}

Creature.id              = 10325
Creature.name            = "thyril"
Creature.level           = 2
Creature.family          = "thyril"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 44
Creature.hp_variance     = 5

Creature.ds_melee        = 32
Creature.ds_bolt         = 14
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 3
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type="claw", as=36, damage_type="slash" },
    { type="bite", as=32, damage_type="puncture" },
}

Creature.spells = {}
Creature.abilities = { "evade_maneuver" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a thyril pelt"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215
}

Creature.roam_rooms = {
    3205, 3206,
    3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217,
    34447
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 170
Creature.max_count       = 2

Creature.description = "The thyril's pale winter coat lets it disappear into the drifted underbrush until it moves.  Its eyes are wide and reflective in the cold light, and every motion suggests the nervous speed of a predator forced to share lean hunting grounds with worse things."

return Creature
