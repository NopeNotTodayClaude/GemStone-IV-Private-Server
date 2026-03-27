-- Creature: myklian
-- Zone: tavaalor | Rambling Meadows Hilltop | Level: 8
-- Armored reptilian predators sunning themselves on the exposed hilltops.
-- High DS, tough hide, worth hunting for their scales.
local Creature = {}

Creature.id             = 7031
Creature.name           = "myklian"
Creature.level          = 8
Creature.family         = "reptile"
Creature.classification = "living"
Creature.body_type      = "quadruped"

Creature.hp_base        = 96
Creature.hp_variance    = 14

-- Combat
Creature.ds_melee       = 96
Creature.ds_bolt        = 70
Creature.td_spiritual   = 24
Creature.td_elemental   = 24
Creature.udf            = 0
Creature.armor_asg      = 6   -- natural scale equivalent of chain mail
Creature.armor_natural  = true

Creature.attacks = {
    { type = "tail_sweep", as = 104, damage_type = "crush" },
    { type = "bite",       as = 100, damage_type = "puncture" },
    { type = "claw",       as  = 96, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = { "fire" }
Creature.resist    = { "cold" }

-- Loot
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = "a myklian scale"
Creature.special_loot = { "a myklian tail tip" }

-- Decay
Creature.decay_seconds = 320
Creature.crumbles      = false
Creature.decay_message = ""

-- Rambling Meadows hilltop only
Creature.spawn_rooms = {
    5995, 5996, 5997, 5998, 5999,
    6000, 6001, 6002, 6003, 6004, 6005, 6006, 6007, 6008, 6009,
}

Creature.roam_rooms = {
    5995, 5996, 5997, 5998, 5999,
    6000, 6001, 6002, 6003, 6004, 6005, 6006, 6007, 6008, 6009,
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 360
Creature.max_count       = 2

return Creature
