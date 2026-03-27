-- Creature: giant rat
-- Zone: WL Catacombs / Sewers  |  Level: 1
local Creature = {}
Creature.id              = 9301
Creature.name            = "giant rat"
Creature.level           = 1
Creature.family          = "rodent"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 26
Creature.hp_variance     = 4
Creature.ds_melee        = 18
Creature.ds_bolt         = 8
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 2
Creature.armor_asg       = 1
Creature.armor_natural   = true
Creature.attacks = {
    { type="bite", as=20, damage_type="puncture" },
    { type="claw", as=16, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "disease_bite",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a rat pelt"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    3938,
    3939,
    3940,
    3941,
    3942,
    3943,
    3944,
    3945,
    3946,
    3947,
    3948,
    3949,
    3950,
    3951,
    3952,
    3953,
    3954,
    3955,
    3956,
    3957,
    3958,
    3959,
    3960,
    3961,
    3962,
    3963,
    3964,
    3965,
    3966,
    3967,
    3968,
    3969,
    3970,
    3971,
    3972,
    3973,
    3974,
    3975,
    3976,
    3977,
    5909,
    5910,
    5911,
    5912
    }
Creature.roam_rooms = {
    3938,
    3939,
    3940,
    3941,
    3942,
    3943,
    3944,
    3945,
    3946,
    3947,
    3948,
    3949,
    3950,
    3951,
    3952,
    3953,
    3954,
    3955,
    3956,
    3957,
    3958,
    3959,
    3960,
    3961,
    3962,
    3963,
    3964,
    3965,
    3966,
    3967,
    3968,
    3969,
    3970,
    3971,
    3972,
    3973,
    3974,
    3975,
    3976,
    3977,
    5909,
    5910,
    5911,
    5912
    }
Creature.roam_chance     = 30
Creature.respawn_seconds = 150
Creature.max_count       = 5
Creature.description = "Near the size of a large housecat, this grey-brown sewer rat has thrived in the damp dark on whatever scraps the catacombs provide.  Yellowed incisors protrude from a twitching muzzle, and the naked pink tail drags behind it on the stone floor.  It has the diseased, feral intensity of something with nothing to lose."
return Creature
