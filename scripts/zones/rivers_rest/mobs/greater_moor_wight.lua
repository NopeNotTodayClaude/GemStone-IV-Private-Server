-- Creature: greater moor wight
-- Zone: Oteska's Haven  |  Level: 39
local Creature = {}
Creature.id              = 10011
Creature.name            = "greater moor wight"
Creature.level           = 39
Creature.family          = "wight"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 492
Creature.hp_variance     = 41
Creature.ds_melee        = 318
Creature.ds_bolt         = 162
Creature.td_spiritual    = 128
Creature.td_elemental    = 128
Creature.udf             = 325
Creature.armor_asg       = 12
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=382, damage_type="slash" },
    { type="bite", as=374, damage_type="puncture" },
    { type="life_drain", as=368, damage_type="cold" },
}
Creature.spells          = {
    { name="wither", cs=198, as=0 },
    { name="dark_catalyst", cs=192, as=0 },
}
Creature.abilities       = {
    "wight_drain",
    "life_drain",
    "disease_touch",
    "aura_of_dread",
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
Creature.skin            = "a wight finger bone"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11667,
    11668,
    11669,
    11671,
    11672,
    11673,
    11674,
    11677,
    11678,
    16147
    }
Creature.roam_rooms      = {
    11667,
    11668,
    11669,
    11671,
    11672,
    11673,
    11674,
    11677,
    11678,
    16147,
    11683,
    11684,
    11685
    }
Creature.roam_chance     = 10
Creature.respawn_seconds = 600
Creature.max_count       = 1
Creature.description     = "Senior in the hierarchy of Oteska's Haven, the greater moor wight carries itself with the terrible authority of the very old dead.  The flesh that remains has the texture of cured leather, drawn tight over bone, and the eyes hold not just hatred but something approaching intelligence.  The draining cold it radiates is perceptible at ten feet and becomes incapacitating at close range."
return Creature
