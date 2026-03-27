-- Creature: giant ant
-- Zone: WL Catacombs / Ant Nest  |  Level: 1
local Creature = {}
Creature.id              = 9303
Creature.name            = "giant ant"
Creature.level           = 1
Creature.family          = "insect"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 30
Creature.hp_variance     = 4
Creature.ds_melee        = 20
Creature.ds_bolt         = 8
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 2
Creature.armor_natural   = true
Creature.attacks = {
    { type="bite", as=22, damage_type="puncture" },
    { type="sting", as=18, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {
    "ant_acid_spray",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "an ant mandible"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    7495,
    7496,
    7497,
    7498,
    7499,
    7502,
    7503,
    7504,
    7505,
    7506,
    7507,
    7508,
    7509,
    7510,
    7511
    }
Creature.roam_rooms = {
    7495,
    7496,
    7497,
    7498,
    7499,
    7502,
    7503,
    7504,
    7505,
    7506,
    7507,
    7508,
    7509,
    7510,
    7511,
    5919,
    5920,
    5921,
    5922
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 150
Creature.max_count       = 1
Creature.description = "The size of a large dog, this giant ant moves with the mechanical efficiency of its kind — every action purposeful, every motion directed by the colony's collective will.  Its black chitinous armor is remarkably tough, and the mandibles that flex at the front of its head can shear through leather with disturbing ease."
return Creature
