-- Creature: fire ogre
-- Zone: Teras Isle / Basalt Flats  |  Level: 28
local Creature = {}
Creature.id              = 10206
Creature.name            = "fire ogre"
Creature.level           = 28
Creature.family          = "ogre"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 345
Creature.hp_variance     = 28
Creature.ds_melee        = 232
Creature.ds_bolt         = 112
Creature.td_spiritual    = 90
Creature.td_elemental    = 90
Creature.udf             = 0
Creature.armor_asg       = 9
Creature.armor_natural   = false
Creature.attacks         = {
    { type="mace", as=338, damage_type="crush" },
    { type="fist", as=330, damage_type="crush" },
    { type="fire_throw", as=320, damage_type="fire" },
}
Creature.spells          = {
    { name="fire_bolt", cs=140, as=0 },
}
Creature.abilities       = {
    "fire_throw",
    "powerful_blow",
    "fire_immunity",
}
Creature.immune          = {
    "fire",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "an ogre tusk"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    12575,
    12576,
    12577,
    12578,
    12579,
    12580,
    12581
    }
Creature.roam_rooms      = {
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    12575,
    12576,
    12577,
    12578,
    12579,
    12580,
    12581,
    14694,
    14695,
    14696
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 480
Creature.max_count       = 2
Creature.description     = "The fire ogre of Teras Isle has adapted to living near active lava flows and geyser fields, and its body temperature registers noticeably above that of most living creatures.  The skin has taken on a reddish-orange tinge and is tougher than standard ogre hide.  It has learned to hurl globs of volcanic matter as a ranged attack, which distinguishes it from its mainland kin in a particularly inconvenient way."
return Creature
