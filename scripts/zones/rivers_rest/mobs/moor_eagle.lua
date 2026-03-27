-- Creature: moor eagle
-- Zone: Shattered Moors  |  Level: 35
local Creature = {}
Creature.id              = 10003
Creature.name            = "moor eagle"
Creature.level           = 35
Creature.family          = "bird"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 442
Creature.hp_variance     = 36
Creature.ds_melee        = 288
Creature.ds_bolt         = 140
Creature.td_spiritual    = 112
Creature.td_elemental    = 112
Creature.udf             = 8
Creature.armor_asg       = 2
Creature.armor_natural   = true
Creature.attacks         = {
    { type="talon", as=342, damage_type="slash" },
    { type="beak", as=335, damage_type="puncture" },
    { type="wing_buffet", as=325, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "diving_strike",
    "sharp_vision",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a moor eagle feather"
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
    11553,
    11611,
    11612,
    11613
    }
Creature.roam_chance     = 25
Creature.respawn_seconds = 480
Creature.max_count       = 2
Creature.description     = "Spanning nearly eight feet wingtip to wingtip, the moor eagle is an apex predator of the open moorland.  Smoke-grey plumage fades to near-black at the wingtips, and the hooked beak has the yellow-orange of old bone.  When it stoops from height, the impact of those talons has been known to stagger a fully armoured warrior."
return Creature
