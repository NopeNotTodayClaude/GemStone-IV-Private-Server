-- Creature: moor witch
-- Zone: Shattered Moors  |  Level: 34
local Creature = {}
Creature.id              = 10002
Creature.name            = "moor witch"
Creature.level           = 34
Creature.family          = "humanoid"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 430
Creature.hp_variance     = 35
Creature.ds_melee        = 278
Creature.ds_bolt         = 132
Creature.td_spiritual    = 110
Creature.td_elemental    = 110
Creature.udf             = 0
Creature.armor_asg       = 5
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=336, damage_type="slash" },
    { type="staff", as=330, damage_type="crush" },
}
Creature.spells          = {
    { name="fire_shard", cs=168, as=0 },
    { name="earthen_fury", cs=162, as=0 },
    { name="curse", cs=158, as=0 },
}
Creature.abilities       = {
    "hag_curse",
    "bog_mire_trap",
    "cackle_fear",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a moor witch fingernail"
Creature.special_loot    = {
    "a gnarled witch's staff",
}
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
    11611,
    11612,
    11613,
    11614
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
    11553,
    11611,
    11612,
    11613,
    11614
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 480
Creature.max_count       = 1
Creature.description     = "Stooped, weathered, and wearing rags that have absorbed decades of moor-damp, the moor witch moves on bare feet that never seem troubled by the sucking mud around her.  One clouded eye and one sharp-bright eye survey the terrain with the specific wariness of something that has survived here through cunning rather than strength.  The crooked staff she carries smells of old magic and older grudges."
return Creature
