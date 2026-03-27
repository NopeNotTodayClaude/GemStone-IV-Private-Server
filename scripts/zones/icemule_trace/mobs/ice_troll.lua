-- Creature: ice troll
-- Zone: Icemule Trace / Glatoph  |  Level: 29
local Creature = {}
Creature.id              = 10306
Creature.name            = "ice troll"
Creature.level           = 29
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 358
Creature.hp_variance     = 29
Creature.ds_melee        = 245
Creature.ds_bolt         = 118
Creature.td_spiritual    = 92
Creature.td_elemental    = 92
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=350, damage_type="slash" },
    { type="bite", as=342, damage_type="puncture" },
    { type="pound", as=335, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "troll_regeneration",
    "ice_skin",
    "cold_immunity",
}
Creature.immune          = {
    "cold",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a troll scalp"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    2558,
    2559,
    2560,
    2561,
    2562,
    2563,
    2564,
    2565,
    2566,
    2567,
    2568,
    2569,
    2570,
    2571,
    3550,
    3551,
    3552,
    3553,
    3554,
    3559,
    3617,
    3678,
    3679,
    3680,
    3681,
    3682,
    4122,
    4123,
    4124
    }
Creature.roam_rooms      = {
    2558,
    2559,
    2560,
    2561,
    2562,
    2563,
    2564,
    2565,
    2566,
    2567,
    2568,
    2569,
    2570,
    2571,
    3550,
    3551,
    3552,
    3553,
    3554,
    3559,
    3617,
    3678,
    3679,
    3680,
    3681,
    3682,
    4122,
    4123,
    4124
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 480
Creature.max_count       = 4
Creature.description     = "The ice troll's skin has incorporated crystals of permafrost ice into its composition over generations of living in sub-zero temperatures.  The effect is an armour-like quality to the hide that is also, incidentally, beautiful in a threatening way — the skin catches light in shifting blue-white patterns.  The regeneration common to all trolls is unimpaired by temperature, which makes fire a necessary tool here more than most places."
return Creature
