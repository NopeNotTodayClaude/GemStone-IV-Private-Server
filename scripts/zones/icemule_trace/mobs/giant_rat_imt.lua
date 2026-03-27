-- Creature: giant rat
-- Zone: Icemule Trace / Snowflake Vale  |  Level: 1
local Creature = {}

Creature.id              = 10323
Creature.name            = "giant rat"
Creature.level           = 1
Creature.family          = "rodent"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 26
Creature.hp_variance     = 4

Creature.ds_melee        = 18
Creature.ds_bolt         = 8
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 2
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type="bite", as=20, damage_type="puncture" },
    { type="claw", as=16, damage_type="slash" },
}

Creature.spells = {}
Creature.abilities = { "disease_bite" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a rat pelt"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202
}

Creature.roam_rooms = {
    3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202,
    3203, 3204, 3205, 3206
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 150
Creature.max_count       = 2

Creature.description = "This snow-hardened giant rat has a greasy grey coat and ice-rimmed whiskers.  It darts between wind-thrown drifts and deadfall with the single-minded focus of something that has learned to survive by stealing food faster than larger predators can stop it."

return Creature
