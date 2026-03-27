-- Creature: kobold shaman
-- Zone: tavaalor | Fearling Pass | Level: 4
-- A wily kobold caster tucked into the ravines and forest stretches of the pass.
local Creature = {}

Creature.id             = 7011
Creature.name           = "kobold shaman"
Creature.level          = 4
Creature.family         = "kobold"
Creature.classification = "living"
Creature.body_type      = "biped"

Creature.hp_base        = 42
Creature.hp_variance    = 6

-- Combat
Creature.ds_melee       = 36
Creature.ds_bolt        = 28
Creature.td_spiritual   = 12
Creature.td_elemental   = 12
Creature.udf            = 0
Creature.armor_asg      = 1
Creature.armor_natural  = false

Creature.attacks = {
    { type = "staff",   as = 48, damage_type = "crush" },
    { type = "dagger",  as = 42, damage_type = "puncture" },
}

Creature.spells    = { "minor_shock", "call_lightning" }
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- Loot
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a tattered kobold skin"
Creature.special_loot = { "a kobold ear" }

-- Decay
Creature.decay_seconds = 200
Creature.crumbles      = false
Creature.decay_message = ""

-- Deeper sections of Fearling Pass — ravines, forest trail, crevasse
Creature.spawn_rooms = {
    10158, 10159, 10160, 10161,
    10162, 10163, 10164, 10165, 10166,
    10167, 10168, 10169, 10170,
}

Creature.roam_rooms = {
    10158, 10159, 10160, 10161,
    10162, 10163, 10164, 10165, 10166,
    10167, 10168, 10169, 10170,
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 240
Creature.max_count       = 1

return Creature
