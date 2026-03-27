-- Creature: deranged sentry
-- Zone: the_citadel / Thurfel's Keep (deep sections)  |  Level: 13
-- Source: https://gswiki.play.net/Deranged_sentry
-- HP: 160 | AS: halberd 114-160 (mid 137) | DS: 100 | bolt: 60 | UDF: 151 | TD: 39-42 (mid 40)
-- ASG: 11 (studded leather) | Body: biped | Classification: living
-- Maneuvers: disarm, tackle, trip | Treasure: coins yes, boxes yes | Skin: a sentry badge
local Creature = {}

Creature.id              = 10441
Creature.name            = "deranged sentry"
Creature.level           = 13
Creature.family          = "humanoid"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 160
Creature.hp_variance     = 16

Creature.ds_melee        = 100
Creature.ds_bolt         = 60
Creature.td_spiritual    = 40
Creature.td_elemental    = 40
Creature.udf             = 151
Creature.armor_asg       = 11
Creature.armor_natural   = false

Creature.attacks = {
    { type = "halberd", as = 137, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = { "disarm_weapon", "tackle", "trip" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a sentry badge"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    11261, 11262, 11263, 11264, 11265,
    11266, 11267, 11268, 11269, 11270,
    11271, 11272, 11273, 11274, 11275,
    11276, 11277, 11278, 11279, 11280,
}

Creature.roam_rooms = {
    11261, 11262, 11263, 11264, 11265,
    11266, 11267, 11268, 11269, 11270,
    11271, 11272, 11273, 11274, 11275,
    11276, 11277, 11278, 11279, 11280,
}

Creature.roam_chance     = 15
Creature.respawn_seconds = 300
Creature.max_count       = 5

Creature.description = "The deranged sentry was a wall guardian once, distinguished by rank and a slightly more elaborate uniform. Whatever happened to its mind has not slowed its halberd. It moves through the deep tunnels in an erratic patrol pattern that serves no tactical logic but covers every approach regardless, and its disarm attempt comes with a reflexive sweep that takes your footing at the same time it takes your weapon."

return Creature
