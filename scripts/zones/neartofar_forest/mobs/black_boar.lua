-- Creature: black boar
-- Zone: Neartofar Forest | Forest, Ridge, and Hillside | Level: 14
local Creature = {}

Creature.id              = 6006
Creature.name            = "black boar"
Creature.level           = 14
Creature.family          = "boar"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 178
Creature.hp_variance     = 13

Creature.ds_melee        = 124
Creature.ds_bolt         = 56
Creature.td_spiritual    = 45
Creature.td_elemental    = 45
Creature.udf             = 5
Creature.armor_asg       = 6
Creature.armor_natural   = true

Creature.attacks = {
    { type = "gore",   as = 172, damage_type = "puncture" },
    { type = "charge", as = 166, damage_type = "crush" },
    { type = "bite",   as = 158, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = { "charge_knockdown", "tough_hide" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a black boar tusk"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    10633, 10634, 10635, 10636, 10637,
    10638, 10639, 10640, 10641,
    10642, 10643, 10644, 10645, 10646, 10647, 10648, 10649
}

Creature.roam_rooms = {
    10633, 10634, 10635, 10636, 10637,
    10638, 10639, 10640, 10641,
    10642, 10643, 10644, 10645, 10646, 10647, 10648, 10649,
    10650, 10651, 10656, 10657
}

Creature.roam_chance     = 16
Creature.respawn_seconds = 340
Creature.max_count       = 2

Creature.description = "Broader, darker, and meaner than its brown-coated cousin, the black boar prowls the Neartofar brush with a constant, simmering aggression.  Matted bristles rise in a ridge along its spine whenever it catches your scent."

return Creature
