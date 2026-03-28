-- snow spectre L9 | icemule_trace / Glatoph upper | ID 10435
local Creature = {}

Creature.id              = 10435
Creature.name            = "snow spectre"
Creature.level           = 9
Creature.family          = "ghost"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 90
Creature.hp_variance     = 9

Creature.ds_melee        = 0
Creature.ds_bolt         = 0
Creature.td_spiritual    = 27
Creature.td_elemental    = 27
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "punch", as = 98, damage_type = "crush" },
}

Creature.spells = {
    { name = "Fear", cs = 50, as = 0, bolt = false },
}
Creature.abilities = {  }
Creature.immune    = { "disease", "poison", "slash", "puncture", "crush" }
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a spectre nail"
Creature.special_loot = {}

Creature.decay_seconds = 60
Creature.crumbles      = true
Creature.decay_message = ""

Creature.spawn_rooms = {
    2585, 2586, 2587, 2588, 2589, 2590, 2591, 2592, 2593, 2594, 2595, 2596, 2597, 2598, 2599
}

Creature.roam_rooms = {
    2585, 2586, 2587, 2588, 2589, 2590, 2591, 2592, 2593, 2594, 2595, 2596, 2597, 2598, 2599
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 4

Creature.description = "The snow spectre is visible as a distortion in the blowing snow — a column of cold that moves against the wind direction and carries a concentrated silence with it. It strikes with a cold fist that hits with more force than physics should allow, and the fear it channels is not a trick or a spell so much as the raw sensation of standing next to something that should not exist."

return Creature
