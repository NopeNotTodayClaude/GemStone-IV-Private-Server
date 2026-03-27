-- Creature: giant rat
-- Zone: tavaalor | Victory Road / Rambling Meadows | Level: 1
-- Oversized vermin rooting through the meadows south of the city.
local Creature = {}

Creature.id             = 7020
Creature.name           = "giant rat"
Creature.level          = 1
Creature.family         = "rodent"
Creature.classification = "living"
Creature.body_type      = "quadruped"

Creature.hp_base        = 16
Creature.hp_variance    = 3

-- Combat
Creature.ds_melee       = 10
Creature.ds_bolt        = 6
Creature.td_spiritual   = 3
Creature.td_elemental   = 3
Creature.udf            = 0
Creature.armor_asg      = 1
Creature.armor_natural  = true

Creature.attacks = {
    { type = "bite",  as = 18, damage_type = "puncture" },
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
Creature.skin        = "a rat pelt"
Creature.special_loot = { "a grey rat tail" }

-- Decay
Creature.decay_seconds = 90
Creature.crumbles      = false
Creature.decay_message = ""

-- Victory Road + lower Rambling Meadows
Creature.spawn_rooms = {
    5950, 5951, 5952, 5953, 5954, 5955,
    5956, 5957, 5958,
    5959, 5960, 5961, 5962, 5963, 5964, 5965, 5966,
}

Creature.roam_rooms = {
    5950, 5951, 5952, 5953, 5954, 5955,
    5956, 5957, 5958,
    5959, 5960, 5961, 5962, 5963, 5964, 5965, 5966,
}

Creature.roam_chance     = 50
Creature.respawn_seconds = 150
Creature.max_count       = 2

return Creature
