-- Creature: wolf
-- Zone: tavaalor | Rambling Meadows | Level: 3
-- Grey wolves roaming the meadows and orchards south of Ta'Vaalor.
local Creature = {}

Creature.id             = 7021
Creature.name           = "wolf"
Creature.level          = 3
Creature.family         = "canine"
Creature.classification = "living"
Creature.body_type      = "quadruped"

Creature.hp_base        = 36
Creature.hp_variance    = 6

-- Combat
Creature.ds_melee       = 30
Creature.ds_bolt        = 20
Creature.td_spiritual   = 9
Creature.td_elemental   = 9
Creature.udf            = 0
Creature.armor_asg      = 1
Creature.armor_natural  = true

Creature.attacks = {
    { type = "bite",  as = 44, damage_type = "puncture" },
    { type = "claw",  as = 38, damage_type = "slash" },
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
Creature.skin        = "a wolf pelt"
Creature.special_loot = { "a wolf fang" }

-- Decay
Creature.decay_seconds = 200
Creature.crumbles      = false
Creature.decay_message = ""

-- Rambling Meadows lower fields + orchard
Creature.spawn_rooms = {
    5959, 5960, 5961, 5962, 5963, 5964, 5965, 5966, 5967, 5968, 5969, 5970, 5971, 5972, 5973,
    5976, 5977, 5978, 5979, 5980, 5981, 5982, 5983, 5984,
}

Creature.roam_rooms = {
    5959, 5960, 5961, 5962, 5963, 5964, 5965, 5966, 5967, 5968, 5969, 5970, 5971, 5972, 5973,
    5976, 5977, 5978, 5979, 5980, 5981, 5982, 5983, 5984,
}

Creature.roam_chance     = 40
Creature.respawn_seconds = 220
Creature.max_count       = 3

return Creature
