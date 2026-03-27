-- Creature: necrotic snake
-- Zone: Marsh Keep  |  Level: 48
local Creature = {}
Creature.id              = 10016
Creature.name            = "necrotic snake"
Creature.level           = 48
Creature.family          = "snake"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "ophidian"
Creature.hp_base         = 578
Creature.hp_variance     = 48
Creature.ds_melee        = 368
Creature.ds_bolt         = 188
Creature.td_spiritual    = 158
Creature.td_elemental    = 158
Creature.udf             = 372
Creature.armor_asg       = 7
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=455, damage_type="puncture" },
    { type="constrict", as=445, damage_type="crush" },
}
Creature.spells          = {
    { name="necrotic_venom", cs=242, as=0 },
}
Creature.abilities       = {
    "necrotic_bite",
    "disease_touch",
    "undead_resilience",
    "constrict",
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
Creature.skin            = "a necrotic snake scale"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11721,
    11722,
    11723,
    11724,
    11725,
    11726,
    11727,
    11728,
    11729,
    11730,
    11731,
    11732,
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
    11721,
    11722,
    11723,
    11724,
    11725,
    11726,
    11727,
    11728,
    11729,
    11730,
    11731,
    11732,
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
Creature.roam_chance     = 12
Creature.respawn_seconds = 660
Creature.max_count       = 4
Creature.description     = "Roughly the thickness of a man's thigh and long enough to encircle the keep's interior pillars, the necrotic snake moves with the fluid economy of all serpents, modified by undeath into something slightly more mechanical.  The scales have darkened to near-black and developed a faint iridescence suggesting the necromantic energies within.  The bite delivers not just trauma but a specific rotting quality that resists ordinary healing."
return Creature
