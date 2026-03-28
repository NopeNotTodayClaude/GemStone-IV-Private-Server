-- Creature: fanged rodent
-- Zone: tavaalor | Catacombs | Level: 1
-- Source: gswiki.play.net/Fanged_rodent
-- Spawns only in the Ta'Vaalor city catacombs (accessed via climb grate)
local Creature = {}

Creature.id             = 7001
Creature.name           = "fanged rodent"
Creature.level          = 1
Creature.family         = "rodent"
Creature.classification = "living"
Creature.body_type      = "quadruped"

Creature.hp_base        = 18
Creature.hp_variance    = 4

Creature.ds_melee       = 12
Creature.ds_bolt        = 8
Creature.td_spiritual   = 3
Creature.td_elemental   = 3
Creature.udf            = 0
Creature.armor_asg      = 1
Creature.armor_natural  = true

Creature.attacks = {
    { type = "bite",  as = 22, damage_type = "puncture" },
    { type = "claw",  as = 18, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a rodent fang"
Creature.special_loot = {
    "a yellowed rodent fang",
}

Creature.decay_seconds = 120
Creature.crumbles      = false
Creature.decay_message = "The fanged rodent's body stiffens and begins to decay."

Creature.description = "The fanged rodent is a large, sleek rat with a tawny brown coat.  Its most notable features are the pair of elongated, yellowed canine teeth that jut from its upper jaw, giving the creature its name."

-- NOTE: One room ID per line — parser requires it
Creature.spawn_rooms = {
    5909,
    5910,
    5911,
    5912,
    5913,
    5914,
    5915,
    5916,
    5917,
    5918,
    5919,
    5920,
    5921,
    5922,
    5923,
    5925,
    5926,
    5927,
    5928,
    5929,
    5932,
    5933,
    5936,
    5939,
    5943,
    5945,
    5946,
    5947,
}

Creature.roam_rooms = {
    5909,
    5910,
    5911,
    5912,
    5913,
    5914,
    5915,
    5916,
    5917,
    5918,
    5919,
    5920,
    5921,
    5922,
    5923,
    5925,
    5926,
    5927,
    5928,
    5929,
    5932,
    5933,
    5936,
    5939,
    5943,
    5945,
    5946,
    5947,
}

Creature.roam_chance     = 40
Creature.respawn_seconds = 150
Creature.max_count       = 4

return Creature
