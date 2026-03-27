-- greater burrow orc L8 | melgorehn_s_valley / Melgorehn's Valley | ID 10431
local Creature = {}

Creature.id              = 10431
Creature.name            = "greater burrow orc"
Creature.level           = 8
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 110
Creature.hp_variance     = 11

Creature.ds_melee        = 86
Creature.ds_bolt         = 45
Creature.td_spiritual    = 24
Creature.td_elemental    = 24
Creature.udf             = 110
Creature.armor_asg       = 8
Creature.armor_natural   = false

Creature.attacks = {
    { type = "short_sword", as = 128, damage_type = "slash" },
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
    3773, 3774, 3775, 3776, 3777, 3778, 3779, 3780, 3781, 3782, 3783, 3784, 3785, 3786, 3787
}

Creature.roam_rooms = {
    3773, 3774, 3775, 3776, 3777, 3778, 3779, 3780, 3781, 3782, 3783, 3784, 3785, 3786, 3787
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 260
Creature.max_count       = 5

Creature.description = "The greater burrow orc is the senior rank in the valley hierarchy and makes no effort to hide it. Its double leather is dark with use and its short sword has been resharpened so many times the blade is narrower than it started. It does not rush. It moves through the tunnels with the unhurried competence of something that has fought in this space every day of its adult life."

return Creature
