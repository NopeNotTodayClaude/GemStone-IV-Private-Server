-- Creature: moor hound
-- Zone: Shattered Moors  |  Level: 33
local Creature = {}
Creature.id              = 10001
Creature.name            = "moor hound"
Creature.level           = 33
Creature.family          = "canine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 422
Creature.hp_variance     = 35
Creature.ds_melee        = 270
Creature.ds_bolt         = 130
Creature.td_spiritual    = 108
Creature.td_elemental    = 108
Creature.udf             = 5
Creature.armor_asg       = 3
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=328, damage_type="puncture" },
    { type="claw", as=322, damage_type="slash" },
}
Creature.spells          = {}
Creature.abilities       = {
    "pack_tactics",
    "howl_of_dread",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a moor hound pelt"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11531,
    11532,
    11533,
    11534,
    11535,
    11536,
    11537,
    11538,
    11539,
    11540,
    11548,
    11549,
    11550,
    11551,
    11552,
    11553
    }
Creature.roam_rooms      = {
    11531,
    11532,
    11533,
    11534,
    11535,
    11536,
    11537,
    11538,
    11539,
    11540,
    11548,
    11549,
    11550,
    11551,
    11552,
    11553
    }
Creature.roam_chance     = 25
Creature.respawn_seconds = 480
Creature.max_count       = 2
Creature.description     = "Built like a mastiff but draped in matted, mud-dark fur the colour of the moors themselves, the moor hound moves with the rolling, ground-eating lope of a creature that has been hunting this terrain its entire life.  Red eyes gleam above jaws that could snap a femur without effort, and its bay carries for considerable distances across the open moor."
return Creature
