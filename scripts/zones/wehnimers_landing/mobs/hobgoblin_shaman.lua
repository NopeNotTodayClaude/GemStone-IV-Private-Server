-- Creature: hobgoblin shaman  |  Zone: wehnimers_landing / Upper Trollfang  |  Level: 7
-- Source: gswiki.play.net/Hobgoblin_shaman
-- HP: 80 | AS: whip/mace 111 AS, bolt 89 AS | DS: 70 | bolt: 45 | TD: 21 | ASG: 2
local Creature = {}

Creature.id              = 9336
Creature.name            = "hobgoblin shaman"
Creature.level           = 7
Creature.family          = "goblin"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 80
Creature.hp_variance     = 8

Creature.ds_melee        = 70
Creature.ds_bolt         = 45
Creature.td_spiritual    = 21
Creature.td_elemental    = 21
Creature.udf             = 95
Creature.armor_asg       = 2
Creature.armor_natural   = false

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
Creature.skin         = "a hobgoblin scalp"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 1196, 1197, 1198, 1199, 1200
}

Creature.roam_rooms = {
    452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 1196, 1197, 1198, 1199, 1200
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 260
Creature.max_count       = 4

Creature.description = "The hobgoblin shaman has learned enough elemental magic to be genuinely dangerous at range and at melee, which means it is dangerous at all distances. The ornaments woven into its matted hair are the bones of things it has killed, and the mace it carries has been wrapped so many times in leather strips that the original weapon is unrecognizable beneath them. It casts first, hits second, and has no clear preference for which kills you."

return Creature
