-- Creature: dark shambler
-- Zone: Vornavis / North Beach Lagoon  |  Level: 17
local Creature = {}
Creature.id              = 10109
Creature.name            = "dark shambler"
Creature.level           = 17
Creature.family          = "shambler"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 210
Creature.hp_variance     = 17
Creature.ds_melee        = 148
Creature.ds_bolt         = 72
Creature.td_spiritual    = 56
Creature.td_elemental    = 56
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=198, damage_type="slash" },
    { type="bite", as=192, damage_type="puncture" },
    { type="pound", as=185, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "disease_touch",
    "sulfurous_appearance",
    "toxic_bite",
}
Creature.immune          = {
    "disease",
    "poison",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a shambler hide"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    7640,
    7641,
    7642,
    7643,
    7644,
    7654,
    7707,
    7712,
    7713,
    7714,
    7715
    }
Creature.roam_rooms      = {
    7640,
    7641,
    7642,
    7643,
    7644,
    7654,
    7707,
    7712,
    7713,
    7714,
    7715
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 380
Creature.max_count       = 1
Creature.description     = "The lagoon dark shambler has adapted to coastal conditions — the skin is roughened by salt spray and the cracked-lava texture common to all shamblers is here given a waterlogged, slightly swollen quality.  It moves through both shallow water and land with equal facility, trailing the sulphurous smoke common to its kind."
return Creature
