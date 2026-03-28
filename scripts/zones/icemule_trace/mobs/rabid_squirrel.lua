-- Creature: rabid squirrel
-- Zone: Icemule Trace / Snowy Forest  |  Level: 2
local Creature = {}
Creature.id              = 10303
Creature.name            = "rabid squirrel"
Creature.level           = 2
Creature.family          = "rodent"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 38
Creature.hp_variance     = 3
Creature.ds_melee        = 30
Creature.ds_bolt         = 12
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=36, damage_type="puncture" },
    { type="scratch", as=30, damage_type="slash" },
}
Creature.spells          = {}
Creature.abilities       = {
    "disease_bite",
    "frenzied_attack",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a squirrel tail"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    3195,
    3196,
    3197,
    3198,
    3199,
    3200,
    3201,
    3202,
    3203,
    3204,
    3205,
    3206,
    3207,
    3208,
    3209,
    3210,
    3211,
    3212,
    3213,
    3214,
    3215,
    3216,
    3217,
    34447
    }
Creature.roam_rooms      = {
    3195,
    3196,
    3197,
    3198,
    3199,
    3200,
    3201,
    3202,
    3203,
    3204,
    3205,
    3206,
    3207,
    3208,
    3209,
    3210,
    3211,
    3212,
    3213,
    3214,
    3215,
    3216,
    3217,
    34447
    }
Creature.roam_chance     = 40
Creature.respawn_seconds = 150
Creature.max_count       = 5
Creature.description     = "Whatever afflicts this squirrel has made it roughly four times more aggressive than the standard model and robbed it of whatever species-level judgment kept the originals from attacking creatures fifty times their size.  The eyes are bloodshot; the tail twitches without stopping; the teeth, when bared, are impressive for a squirrel.  The foam at the corners of the mouth is the most obvious diagnostic clue."
return Creature
