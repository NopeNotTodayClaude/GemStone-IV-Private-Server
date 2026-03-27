-- Creature: coyote
-- Zone: Rambling Meadows  |  Level: 5
local Creature = {}

Creature.id              = 9108
Creature.name            = "coyote"
Creature.level           = 5
Creature.family          = "canine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 74
Creature.hp_variance     = 7

Creature.ds_melee        = 58
Creature.ds_bolt         = 28
Creature.td_spiritual    = 15
Creature.td_elemental    = 15
Creature.udf             = 4
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type="bite", as=76, damage_type="puncture" },
    { type="claw", as=70, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "pack_tactics",
}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a coyote pelt"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    5959,
    5960,
    5961,
    5962,
    5963,
    5964,
    5965,
    5966,
    5967,
    5968,
    5969,
    5970,
    5971,
    5972,
    5973,
    5956,
    5957,
    5958,
    6010
    }
Creature.roam_rooms = {
    5959,
    5960,
    5961,
    5962,
    5963,
    5964,
    5965,
    5966,
    5967,
    5968,
    5969,
    5970,
    5971,
    5972,
    5973,
    5956,
    5957,
    5958,
    6010,
    5976,
    5977,
    5978
    }

Creature.roam_chance     = 35
Creature.respawn_seconds = 220
Creature.max_count       = 2

Creature.description = "Lean and angular with a grizzled tan coat fading to pale at the muzzle and belly, the coyote watches with sharp yellow eyes that miss very little.  It moves in a ground-eating lope that disguises its actual speed, and its ears swivel independently to track sounds.  Alone it is cautious; with others of its kind it grows bold."

return Creature
