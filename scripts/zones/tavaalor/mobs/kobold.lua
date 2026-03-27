-- Creature: kobold
-- Zone: tavaalor | Fearling Pass | Level: 2
-- Scavenging lizard-folk that lurk along the rocky pass north of the city.
local Creature = {}

Creature.id             = 7010
Creature.name           = "kobold"
Creature.level          = 2
Creature.family         = "kobold"
Creature.classification = "living"
Creature.body_type      = "biped"

Creature.hp_base        = 24
Creature.hp_variance    = 5

-- Combat
Creature.ds_melee       = 22
Creature.ds_bolt        = 16
Creature.td_spiritual   = 6
Creature.td_elemental   = 6
Creature.udf            = 0
Creature.armor_asg      = 2
Creature.armor_natural  = false

Creature.attacks = {
    { type = "dagger",  as = 32, damage_type = "puncture" },
    { type = "handaxe", as = 28, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- Loot
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = true
Creature.skin        = "a tattered kobold skin"
Creature.special_loot = { "a kobold ear" }

-- Decay
Creature.decay_seconds = 180
Creature.crumbles      = false
Creature.decay_message = ""

-- Fearling Pass rooms
Creature.spawn_rooms = {
    3557, 6101,
    10121, 10122, 10123,
    10158, 10159, 10160, 10161,
    10162, 10163, 10164, 10165,
}

Creature.roam_rooms = {
    3557, 6101,
    10121, 10122, 10123,
    10158, 10159, 10160, 10161,
    10162, 10163, 10164, 10165,
}

Creature.roam_chance     = 35
Creature.respawn_seconds = 180
Creature.max_count       = 1

return Creature
