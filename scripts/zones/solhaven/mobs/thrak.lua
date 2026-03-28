-- Creature: thrak
-- Zone: Vornavis / Coastal Cliffs  |  Level: 8
local Creature = {}
Creature.id              = 10104
Creature.name            = "thrak"
Creature.level           = 8
Creature.family          = "thrak"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 115
Creature.hp_variance     = 9
Creature.ds_melee        = 78
Creature.ds_bolt         = 38
Creature.td_spiritual    = 24
Creature.td_elemental    = 24
Creature.udf             = 0
Creature.armor_asg       = 5
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=112, damage_type="slash" },
    { type="bite", as=106, damage_type="puncture" },
    { type="tail_slap", as=100, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "armoured_hide",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a thrak hide"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
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
    7681
    }
Creature.roam_rooms      = {
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
    7681
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 240
Creature.max_count       = 2
Creature.description     = "Bipedal, broad-shouldered, and armoured in overlapping scales of dark bronze, the thrak combines the musculature of a fighting creature with the natural protection of a reptile.  It moves with a side-to-side sway that belies the speed of its actual strikes.  The tail is prehensile and has been known to trip opponents at inopportune moments."
return Creature
