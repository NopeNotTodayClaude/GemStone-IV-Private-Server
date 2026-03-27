-- Creature: lesser burrow orc  |  Zone: melgorehn_s_valley / Melgorehn's Valley  |  Level: 7
-- Source: gswiki.play.net/Lesser_burrow_orc
-- HP: 100 | AS: short sword 127 AS | DS: 90 | bolt: 40 | TD: 21 | ASG: 6
local Creature = {}

Creature.id              = 10427
Creature.name            = "lesser burrow orc"
Creature.level           = 7
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 100
Creature.hp_variance     = 10

Creature.ds_melee        = 90
Creature.ds_bolt         = 40
Creature.td_spiritual    = 21
Creature.td_elemental    = 21
Creature.udf             = 116
Creature.armor_asg       = 6
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
Creature.skin         = "an orc ear"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3766, 3767, 3768, 3769, 3770, 3771, 3772
}

Creature.roam_rooms = {
    3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3766, 3767, 3768, 3769, 3770, 3771, 3772
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 240
Creature.max_count       = 6

Creature.description = "The lesser burrow orc has adapted to underground fighting: shorter, wider, and capable of swinging a short sword in a tunnel where a taller weapon would catch the ceiling. Its skin has the grey-green tone of something that rarely sees sunlight, and its eyes have expanded to compensate. It moves through the valley passages with an ease that suggests it knows every turn by memory."

return Creature
