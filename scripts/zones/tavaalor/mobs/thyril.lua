-- Creature: thyril
-- Zone: tavaalor | Fearling Pass Deep | Level: 7
-- Cunning predators lurking in the forested stretches of Fearling Pass.
-- Fast, aggressive, hard to hit.
local Creature = {}

Creature.id             = 7030
Creature.name           = "thyril"
Creature.level          = 7
Creature.family         = "thyril"
Creature.classification = "living"
Creature.body_type      = "quadruped"

Creature.hp_base        = 82
Creature.hp_variance    = 12

-- Combat
Creature.ds_melee       = 82
Creature.ds_bolt        = 58
Creature.td_spiritual   = 21
Creature.td_elemental   = 21
Creature.udf            = 5
Creature.armor_asg      = 2
Creature.armor_natural  = true

Creature.attacks = {
    { type = "claw",  as = 94, damage_type = "slash" },
    { type = "bite",  as = 88, damage_type = "puncture" },
    { type = "charge", as = 80, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = { "evade_maneuver" }
Creature.immune    = {}
Creature.resist    = {}

-- Loot
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a thyril pelt"
Creature.special_loot = {}

-- Decay
Creature.decay_seconds = 280
Creature.crumbles      = false
Creature.decay_message = ""

-- Deep Fearling Pass: forest trail, ridgeline
Creature.spawn_rooms = {
    10162, 10163, 10164, 10165, 10166,
    10167, 10168, 10169, 10170,
    10270, 15931,
}

Creature.roam_rooms = {
    10162, 10163, 10164, 10165, 10166,
    10167, 10168, 10169, 10170,
    10270, 15931,
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 300
Creature.max_count       = 1

return Creature
