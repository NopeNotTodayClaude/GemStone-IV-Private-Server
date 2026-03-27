-- Creature: manticore
-- Zone: Vornavis / Coastal Cliffs  |  Level: 9
local Creature = {}
Creature.id              = 10105
Creature.name            = "manticore"
Creature.level           = 9
Creature.family          = "manticore"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 128
Creature.hp_variance     = 10
Creature.ds_melee        = 88
Creature.ds_bolt         = 45
Creature.td_spiritual    = 27
Creature.td_elemental    = 27
Creature.udf             = 5
Creature.armor_asg       = 5
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=122, damage_type="slash" },
    { type="bite", as=116, damage_type="puncture" },
    { type="tail_spike", as=110, damage_type="puncture" },
}
Creature.spells          = {}
Creature.abilities       = {
    "tail_spike_volley",
    "pounce_maneuver",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a manticore spine"
Creature.special_loot    = {
    "a manticore tail spike",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
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
Creature.roam_chance     = 15
Creature.respawn_seconds = 260
Creature.max_count       = 2
Creature.description     = "The body of a lion, the wings of a bat too small to actually carry it, and the face of a man stretched wrong — the manticore defies comfortable categorization.  The tail is tipped with a cluster of bone spines that it can launch with surprising velocity and accuracy.  The face is the worst part: the features are recognizably humanoid but arranged in an expression of permanent, gleeful cruelty."
return Creature
