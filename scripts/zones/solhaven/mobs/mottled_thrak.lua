-- mottled thrak L8 | solhaven / Coastal Cliffs upper (thrak territory) | ID 10432
local Creature = {}

Creature.id              = 10432
Creature.name            = "mottled thrak"
Creature.level           = 8
Creature.family          = "reptilian"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 130
Creature.hp_variance     = 13

Creature.ds_melee        = 65
Creature.ds_bolt         = 40
Creature.td_spiritual    = 24
Creature.td_elemental    = 24
Creature.udf             = 95
Creature.armor_asg       = 12
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 125, damage_type = "puncture" },
}

Creature.spells = {

}
Creature.abilities = {  }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a mottled thrak hide"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    7707, 7712, 7713, 7714, 7715, 7716, 7717, 7718, 7719, 7720, 7721, 7722, 7723, 7724, 7725
}

Creature.roam_rooms = {
    7707, 7712, 7713, 7714, 7715, 7716, 7717, 7718, 7719, 7720, 7721, 7722, 7723, 7724, 7725
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 4

Creature.description = "The mottled thrak is identified by the broken camouflage pattern of olive and rust that covers its scales — less elegant than the coastal thrak's uniform colouration, and considerably meaner in temperament. Where the standard thrak is an ambush predator, the mottled variant charges directly. Its armoured hide makes it indifferent to most glancing blows."

return Creature
