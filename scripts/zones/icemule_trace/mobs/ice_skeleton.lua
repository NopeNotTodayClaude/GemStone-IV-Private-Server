-- Creature: ice skeleton
-- Zone: Icemule Trace / Glatoph  |  Level: 3
local Creature = {}
Creature.id              = 10308
Creature.name            = "ice skeleton"
Creature.level           = 3
Creature.family          = "skeleton"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 52
Creature.hp_variance     = 4
Creature.ds_melee        = 34
Creature.ds_bolt         = 16
Creature.td_spiritual    = 10
Creature.td_elemental    = 10
Creature.udf             = 45
Creature.armor_asg       = 6
Creature.armor_natural   = false
Creature.attacks         = {
    { type="broadsword", as=52, damage_type="slash" },
    { type="frozen_touch", as=46, damage_type="cold" },
}
Creature.spells          = {}
Creature.abilities       = {
    "undead_resilience",
    "cold_aura",
}
Creature.immune          = {
    "disease",
    "poison",
    "cold",
}
Creature.resist          = {
    "pierce",
    "slash",
}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a skeleton skull"
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
    3678,
    3679,
    3680,
    3681,
    3682,
    4122
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
    3678,
    3679,
    3680,
    3681,
    3682,
    4122
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 200
Creature.max_count       = 2
Creature.description     = "Ordinary skeletal undead, save that each of the bones is coated in a thick frost that gives the whole a blue-white appearance and a cracking, splintering sound with each movement.  The cold it radiates extends several feet and is genuinely uncomfortable at close range.  The touch of the frozen fingers delivers frostbite that lingers beyond the initial contact."
return Creature
