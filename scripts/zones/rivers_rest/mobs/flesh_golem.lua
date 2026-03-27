-- Creature: flesh golem
-- Zone: Marsh Keep  |  Level: 50
local Creature = {}
Creature.id              = 10017
Creature.name            = "flesh golem"
Creature.level           = 50
Creature.family          = "golem"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 600
Creature.hp_variance     = 50
Creature.ds_melee        = 380
Creature.ds_bolt         = 192
Creature.td_spiritual    = 162
Creature.td_elemental    = 162
Creature.udf             = 385
Creature.armor_asg       = 14
Creature.armor_natural   = false
Creature.attacks         = {
    { type="fist", as=475, damage_type="crush" },
    { type="slam", as=468, damage_type="crush" },
    { type="grab", as=460, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "undead_resilience",
    "crushing_grip",
    "immunity_to_stun",
    "golem_slam",
}
Creature.immune          = {
    "disease",
    "poison",
    "cold",
    "electricity",
}
Creature.resist          = {
    "fire",
    "slash",
    "pierce",
}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a golem flesh chunk"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11733,
    11734,
    11735,
    11736,
    11737,
    11738,
    11739,
    11740,
    11741,
    11742,
    11743,
    11744,
    11745,
    11746,
    16179,
    16181,
    16209,
    16210,
    16213,
    17692
    }
Creature.roam_rooms      = {
    11733,
    11734,
    11735,
    11736,
    11737,
    11738,
    11739,
    11740,
    11741,
    11742,
    11743,
    11744,
    11745,
    11746,
    16179,
    16181,
    16209,
    16210,
    16213,
    17692
    }
Creature.roam_chance     = 5
Creature.respawn_seconds = 720
Creature.max_count       = 2
Creature.description     = "The flesh golem was assembled from the worst parts of the Marsh Keep's dead — not the cleanest or most intact, but the largest and densest.  The result is a patchwork giant of mismatched limbs and torsos, held together by dark stitching and darker magic.  There is no face in any recognizable sense, just a mass of layered features that has been pressed together and given crude function.  It does not react to pain, because it does not feel it."
return Creature
