-- Creature: mongrel kobold
-- Zone: Vornavis / Coastal Cliffs  |  Level: 4
local Creature = {}
Creature.id              = 10102
Creature.name            = "mongrel kobold"
Creature.level           = 4
Creature.family          = "kobold"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 60
Creature.hp_variance     = 5
Creature.ds_melee        = 42
Creature.ds_bolt         = 22
Creature.td_spiritual    = 12
Creature.td_elemental    = 12
Creature.udf             = 0
Creature.armor_asg       = 3
Creature.armor_natural   = false
Creature.attacks         = {
    { type="shortsword", as=62, damage_type="slash" },
    { type="handaxe", as=58, damage_type="slash" },
}
Creature.spells          = {}
Creature.abilities       = {}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a kobold ear"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    486,
    487,
    488,
    489,
    490,
    491,
    492,
    493,
    494,
    495,
    496,
    497,
    498,
    499,
    500,
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    508,
    509,
    510,
    511,
    512,
    513,
    514,
    515,
    516,
    517,
    518,
    519,
    520,
    521,
    522,
    523,
    524,
    525,
    7601,
    7673,
    7674,
    7675,
    7676,
    7677,
    7678,
    7679,
    7680,
    7681,
    213,
    214,
    215,
    216,
    217,
    218,
    219,
    421
    }
Creature.roam_rooms      = {
    486,
    487,
    488,
    489,
    490,
    491,
    492,
    493,
    494,
    495,
    496,
    497,
    498,
    499,
    500,
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    508,
    509,
    510,
    511,
    512,
    513,
    514,
    515,
    516,
    517,
    518,
    519,
    520,
    521,
    522,
    523,
    524,
    525,
    7601,
    7673,
    7674,
    7675,
    7676,
    7677,
    7678,
    7679,
    7680,
    7681,
    213,
    214,
    215,
    216,
    217,
    218,
    219,
    421
    }
Creature.roam_chance     = 28
Creature.respawn_seconds = 180
Creature.max_count       = 8
Creature.description     = "Broader and meaner than the common coastal kobold, the mongrel kobold has the look of something with a more complicated ancestry.  The scales are a mottled brown-grey rather than the standard yellow, and it carries weapons with the familiarity of regular use.  The malice in its small orange eyes is genuine rather than reflexive."
return Creature
