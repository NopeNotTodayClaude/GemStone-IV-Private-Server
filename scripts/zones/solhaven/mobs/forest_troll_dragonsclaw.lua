-- Creature: forest troll
-- Zone: Vornavis / Lower Dragonsclaw  |  Level: 14
local Creature = {}
Creature.id              = 10115
Creature.name            = "forest troll"
Creature.level           = 14
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 180
Creature.hp_variance     = 15
Creature.ds_melee        = 133
Creature.ds_bolt         = 63
Creature.td_spiritual    = 46
Creature.td_elemental    = 46
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=177, damage_type="slash" },
    { type="bite", as=170, damage_type="puncture" },
    { type="pound", as=165, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "troll_regeneration",
    "rend",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a troll hide"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    444,
    445,
    446,
    447,
    448,
    449,
    1256,
    1257,
    1258,
    6259,
    6260,
    6261,
    6262,
    6961
    }
Creature.roam_rooms      = {
    444,
    445,
    446,
    447,
    448,
    449,
    1256,
    1257,
    1258,
    6259,
    6260,
    6261,
    6262,
    6961
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 360
Creature.max_count       = 2
Creature.description     = "Bark-rough skin in mottled grey-green, proportionally enormous arms, and a face that is all aggression and hunger — the Dragonsclaw forest troll is identical to its Upper Trollfang kin in all relevant respects.  Like all trolls it regenerates wounds with unsettling speed; unlike some hunting areas, fire is hard to come by in the forested lower cliffs."
return Creature
