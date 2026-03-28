-- crazed canine L10 | cliffwalk / Cliffwalk | ID 10436
local Creature = {}

Creature.id              = 10436
Creature.name            = "crazed canine"
Creature.level           = 10
Creature.family          = "canine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 100
Creature.hp_variance     = 10

Creature.ds_melee        = 80
Creature.ds_bolt         = 45
Creature.td_spiritual    = 30
Creature.td_elemental    = 30
Creature.udf             = 90
Creature.armor_asg       = 6
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 118, damage_type = "puncture" },
}

Creature.spells = {

}
Creature.abilities = { "leap_maneuver" }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a rotted canine"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    29120, 29124, 29128, 29129, 29131, 29133, 29134, 29217, 29218, 29219, 29220, 29221, 29222
}

Creature.roam_rooms = {
    29120, 29124, 29128, 29129, 29131, 29133, 29134, 29217, 29218, 29219, 29220, 29221, 29222
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 5

Creature.description = "The crazed canine is large, fast, and has clearly been feral long enough that the domesticated animal underneath is entirely theoretical. Its eyes are wrong — too bright, tracking too many things at once — and it moves in short stops and starts rather than a straight line. The leap it delivers from a crouch covers more ground than the approach distance would suggest."

return Creature
