-- Creature: black bear
-- Zone: tavaalor | Rambling Meadows Upper | Level: 5
-- Heavy bruisers patrolling the upper fields and hilltops of the meadows.
local Creature = {}

Creature.id             = 7022
Creature.name           = "black bear"
Creature.level          = 5
Creature.family         = "bear"
Creature.classification = "living"
Creature.body_type      = "quadruped"

Creature.hp_base        = 68
Creature.hp_variance    = 10

-- Combat
Creature.ds_melee       = 52
Creature.ds_bolt        = 34
Creature.td_spiritual   = 15
Creature.td_elemental   = 15
Creature.udf            = 0
Creature.armor_asg      = 3
Creature.armor_natural  = true

Creature.attacks = {
    { type = "claw",  as = 68, damage_type = "slash" },
    { type = "pound", as = 60, damage_type = "crush" },
    { type = "bite",  as = 62, damage_type = "puncture" },
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
Creature.skin        = "a bear skin"
Creature.special_loot = { "a bear claw" }

-- Decay
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- Rambling Meadows upper fields + hilltop
Creature.spawn_rooms = {
    5975,
    5985, 5986, 5987, 5988, 5989, 5990, 5991, 5992, 5993,
    5995, 5996, 5997, 5998, 5999,
    6000, 6001, 6002, 6003, 6004, 6005, 6006, 6007, 6008, 6009, 6010,
}

Creature.roam_rooms = {
    5975,
    5985, 5986, 5987, 5988, 5989, 5990, 5991, 5992, 5993,
    5995, 5996, 5997, 5998, 5999,
    6000, 6001, 6002, 6003, 6004, 6005, 6006, 6007, 6008, 6009, 6010,
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 300
Creature.max_count       = 3

return Creature
