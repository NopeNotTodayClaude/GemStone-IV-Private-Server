-- Creature: lesser moor wight
-- Zone: Miasmal Forest  |  Level: 37
local Creature = {}
Creature.id              = 10007
Creature.name            = "lesser moor wight"
Creature.level           = 37
Creature.family          = "wight"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 465
Creature.hp_variance     = 38
Creature.ds_melee        = 302
Creature.ds_bolt         = 152
Creature.td_spiritual    = 122
Creature.td_elemental    = 122
Creature.udf             = 310
Creature.armor_asg       = 10
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=362, damage_type="slash" },
    { type="life_drain", as=354, damage_type="cold" },
}
Creature.spells          = {
    { name="wither", cs=182, as=0 },
}
Creature.abilities       = {
    "wight_drain",
    "life_drain",
    "disease_touch",
}
Creature.immune          = {
    "disease",
    "poison",
}
Creature.resist          = {
    "cold",
}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a wight bone"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11631,
    11632,
    11633,
    11634,
    11635,
    11636,
    11637,
    11638,
    11639,
    11640,
    11641,
    11642,
    11643,
    11644,
    11645,
    11650,
    11651,
    11652,
    11653,
    11654,
    11655,
    11656,
    11657,
    16122,
    16124,
    16127,
    22218,
    22219,
    11647,
    11648,
    11649,
    11658,
    11659
    }
Creature.roam_rooms      = {
    11631,
    11632,
    11633,
    11634,
    11635,
    11636,
    11637,
    11638,
    11639,
    11640,
    11641,
    11642,
    11643,
    11644,
    11645,
    11650,
    11651,
    11652,
    11653,
    11654,
    11655,
    11656,
    11657,
    16122,
    16124,
    16127,
    22218,
    22219,
    11647,
    11648,
    11649,
    11658,
    11659
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 540
Creature.max_count       = 3
Creature.description     = "Dragged from whatever death claimed it by the necromantic energies saturating the miasmal forest, the lesser moor wight is more desiccated ruin than animated corpse.  Peat-stained bones show through gaps in dried flesh, and the movement is driven by a cold intention rather than life.  The draining touch it delivers is unmistakeable — a cold that reaches past the skin directly into vitality."
return Creature
