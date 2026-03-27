-- Creature: spectral black warhorse
-- Zone: Shattered Moors  |  Level: 35
local Creature = {}
Creature.id              = 10004
Creature.name            = "spectral black warhorse"
Creature.level           = 35
Creature.family          = "horse"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "quadruped"
Creature.hp_base         = 445
Creature.hp_variance     = 37
Creature.ds_melee        = 295
Creature.ds_bolt         = 148
Creature.td_spiritual    = 118
Creature.td_elemental    = 82
Creature.udf             = 295
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="spectral_trample", as=348, damage_type="crush" },
    { type="shadow_bite", as=340, damage_type="puncture" },
}
Creature.spells          = {}
Creature.abilities       = {
    "spirit_strike",
    "fear_aura",
    "spectral_charge",
    "phase_through_terrain",
}
Creature.immune          = {
    "disease",
    "poison",
    "cold",
}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = ""
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = true
Creature.decay_message   = "dissolves into a cloud of black vapor."
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
    11553,
    11611,
    11612,
    11613,
    11614,
    11615,
    11616
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
    11614,
    11615,
    11616
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 540
Creature.max_count       = 3
Creature.description     = "Where a living warhorse would be magnificent, the spectral black warhorse is magnificent and terrible.  Its form is absolute darkness shaped like a horse in motion, mane and tail streaming with shadow rather than hair.  The hooves make no sound on the moor — it is the silence of its passage that first announces its approach, a deadening of ambient sound that something living simply doesn't cause."
return Creature
