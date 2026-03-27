-- Creature: greater kappa  |  Zone: solhaven / Coastal Cliffs  |  Level: 7
-- Source: gswiki.play.net/Greater_kappa
-- HP: 100 | AS: handaxe 107 AS | DS: 31 | bolt: 20 | TD: 21 | ASG: 1N
local Creature = {}

Creature.id              = 10425
Creature.name            = "greater kappa"
Creature.level           = 7
Creature.family          = "reptilian"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 100
Creature.hp_variance     = 10

Creature.ds_melee        = 31
Creature.ds_bolt         = 20
Creature.td_spiritual    = 21
Creature.td_elemental    = 21
Creature.udf             = 105
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {

}

Creature.spells = {

}
Creature.abilities = {  }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a kappa shell"
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
Creature.respawn_seconds = 240
Creature.max_count       = 5

Creature.description = "The greater kappa stands taller than a man and smells powerfully of brine and mud. Its turtle-like shell has been battered into a pattern of old dents and scrapes that tell something of its history. It carries a handaxe with the casual grip of something that has held it for a very long time, and it moves through the coastal rocks with the confident footing of an animal that has never slipped."

return Creature
