-- Creature: black bear
-- Zone: Neartofar Forest | Hillside & Ridge | Level: 16
-- Retail black bears belong in Neartofar, not Rambling Meadows.
local Creature = {}

Creature.id             = 7022
Creature.name           = "black bear"
Creature.level          = 16
Creature.family         = "bear"
Creature.classification = "living"
Creature.body_type      = "quadruped"

Creature.hp_base        = 188
Creature.hp_variance    = 15

-- Combat
Creature.ds_melee       = 138
Creature.ds_bolt        = 60
Creature.td_spiritual   = 50
Creature.td_elemental   = 50
Creature.udf            = 0
Creature.armor_asg      = 3
Creature.armor_natural  = true

Creature.attacks = {
    { type = "claw",  as = 184, damage_type = "slash" },
    { type = "pound", as = 176, damage_type = "crush" },
    { type = "bite",  as = 178, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- Loot
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a black bear pelt"
Creature.special_loot = { "a bear claw" }

-- Decay
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    10638, 10639, 10640, 10641,
    10643, 10644,
    10645, 10646, 10647, 10648, 10649,
    10650, 10651, 10652, 10653, 10654, 10655,
    10656, 10657, 10658, 10659
}

Creature.roam_rooms = {
    10638, 10639, 10640, 10641,
    10642, 10643, 10644,
    10645, 10646, 10647, 10648, 10649,
    10650, 10651, 10652, 10653, 10654, 10655,
    10656, 10657, 10658, 10659,
    10660, 10661
}

Creature.roam_chance     = 18
Creature.respawn_seconds = 340
Creature.max_count       = 2

return Creature
