-- Creature: ice hound
-- Zone: Icemule Trace / Icy Ravine  |  Level: 24
local Creature = {}
Creature.id              = 10317
Creature.name            = "ice hound"
Creature.level           = 24
Creature.family          = "canine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 295
Creature.hp_variance     = 24
Creature.ds_melee        = 205
Creature.ds_bolt         = 98
Creature.td_spiritual    = 76
Creature.td_elemental    = 76
Creature.udf             = 5
Creature.armor_asg       = 7
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=290, damage_type="puncture" },
    { type="claw", as=282, damage_type="slash" },
    { type="freeze_bite", as=275, damage_type="cold" },
}
Creature.spells          = {}
Creature.abilities       = {
    "pack_tactics",
    "cold_immunity",
    "freeze_bite",
    "howl_of_dread",
}
Creature.immune          = {
    "cold",
}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "an ice hound pelt"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    2571,
    3550,
    3551,
    3552,
    3553,
    3554,
    3559,
    3617,
    3678,
    3679,
    3680,
    3681,
    3682,
    4122,
    4123,
    4124
    }
Creature.roam_rooms      = {
    2571,
    3550,
    3551,
    3552,
    3553,
    3554,
    3559,
    3617,
    3678,
    3679,
    3680,
    3681,
    3682,
    4122,
    4123,
    4124
    }
Creature.roam_chance     = 25
Creature.respawn_seconds = 420
Creature.max_count       = 2
Creature.description     = "The ice hound appears to be an ordinary large dog until the temperature around it registers — which is about when the frost-rime coating its fur becomes visible, and the cloud of frozen breath from its flanks even while it is not panting becomes apparent.  The bite delivers frostbite as well as trauma, and the pack tactics of the species are as effective here as in warmer climates."
return Creature
