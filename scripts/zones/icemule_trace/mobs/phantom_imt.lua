-- Creature: phantom
-- Zone: Icemule Trace / Snowflake Vale Clearings  |  Level: 2
local Creature = {}

Creature.id              = 10327
Creature.name            = "phantom"
Creature.level           = 2
Creature.family          = "ghost"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 42
Creature.hp_variance     = 5

Creature.ds_melee        = -23
Creature.ds_bolt         = -24
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 26
Creature.armor_asg       = 5
Creature.armor_natural   = false

Creature.attacks = {
    { type="closed_fist", as=28, damage_type="crush" },
}

Creature.spells = {
    { name = "Minor Shock (901)", cs = 0, as = 35, bolt = true },
}

Creature.abilities = {}
Creature.immune = {
    "disease",
    "poison",
}
Creature.resist = {
    "pierce",
    "slash",
    "crush",
}

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = ""
Creature.special_loot = {}

Creature.decay_seconds = 60
Creature.crumbles      = true
Creature.decay_message = ""

Creature.spawn_rooms = {
    3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 34447
}

Creature.roam_rooms = {
    3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 34447
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 180
Creature.max_count       = 1

Creature.description = "A pale outline suspended in the blowing snow, the phantom drifts through the clearings as if it were retracing a path it walked in life.  The cold around it is more spiritual than physical, a pressure that settles into the lungs."

return Creature
