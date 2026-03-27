-- Creature: elder boar
-- Zone: Lunule Weald / Knoll  |  Level: 14
local Creature = {}
Creature.id              = 9503
Creature.name            = "elder boar"
Creature.level           = 14
Creature.family          = "boar"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 175
Creature.hp_variance     = 13
Creature.ds_melee        = 125
Creature.ds_bolt         = 55
Creature.td_spiritual    = 45
Creature.td_elemental    = 45
Creature.udf             = 6
Creature.armor_asg       = 6
Creature.armor_natural   = true
Creature.attacks = {
    { type="gore", as=172, damage_type="puncture" },
    { type="charge", as=165, damage_type="crush" },
    { type="bite", as=158, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {
    "charge_knockdown",
    "toughskin",
    "powerful_gore",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "an elder boar tusk"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    10545,
    10546,
    10552,
    10553,
    10554,
    10555
    }
Creature.roam_rooms = {
    10545,
    10546,
    10552,
    10553,
    10554,
    10555,
    10556,
    10557,
    10558,
    10547,
    10559,
    10560
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 340
Creature.max_count       = 1
Creature.description = "Old enough that its tusks have grown past all proportion, curling back nearly to its eye sockets, the elder boar carries scars from a lifetime of territorial disputes and predator encounters.  Dense, dark bristles have gone grey at the muzzle and shoulders, and the animal moves with the unhurried confidence of something that has never lost a fight it committed to."
return Creature
