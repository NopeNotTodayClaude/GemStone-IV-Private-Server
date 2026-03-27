-- Creature: ghost wolf
-- Zone: Icemule Trace / Tundra  |  Level: 16
local Creature = {}
Creature.id              = 10304
Creature.name            = "ghost wolf"
Creature.level           = 16
Creature.family          = "shade"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "quadruped"
Creature.hp_base         = 200
Creature.hp_variance     = 16
Creature.ds_melee        = 148
Creature.ds_bolt         = 72
Creature.td_spiritual    = 52
Creature.td_elemental    = 35
Creature.udf             = 178
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="shadow_bite", as=196, damage_type="puncture" },
    { type="shadow_claw", as=188, damage_type="slash" },
}
Creature.spells          = {}
Creature.abilities       = {
    "spirit_strike",
    "shadow_meld",
    "fear_howl",
    "pack_tactics",
}
Creature.immune          = {
    "disease",
    "poison",
    "cold",
}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = ""
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = true
Creature.decay_message   = "fades into a wisp of frozen air."
Creature.spawn_rooms     = {
    3211,
    3212,
    3213,
    3214,
    3215,
    3216,
    3217,
    34447,
    2558,
    2559,
    2560,
    2561
    }
Creature.roam_rooms      = {
    3211,
    3212,
    3213,
    3214,
    3215,
    3216,
    3217,
    34447,
    2558,
    2559,
    2560,
    2561
    }
Creature.roam_chance     = 22
Creature.respawn_seconds = 360
Creature.max_count       = 1
Creature.description     = "The ghost wolf of the Icemule tundra is the cold-climate counterpart of the wolfshade — absolute whiteness shaped like a wolf, visible only because snow and ice fail to show through it.  The howl it produces resonates at a frequency that goes beyond sound into something felt in the sternum.  Packs of them have been seen moving across the tundra at night, leaving no tracks."
return Creature
