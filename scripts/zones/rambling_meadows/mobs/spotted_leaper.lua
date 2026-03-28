-- Creature: spotted leaper
-- Zone: Rambling Meadows  |  Level: 4
local Creature = {}

Creature.id              = 9107
Creature.name            = "spotted leaper"
Creature.level           = 4
Creature.family          = "leaper"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 64
Creature.hp_variance     = 6

Creature.ds_melee        = 44
Creature.ds_bolt         = 20
Creature.td_spiritual    = 12
Creature.td_elemental    = 12
Creature.udf             = 3
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type="claw", as=66, damage_type="slash" },
    { type="bite", as=60, damage_type="puncture" },
    { type="pounce", as=58, damage_type="crush" },
}
Creature.spells = {}
Creature.abilities = {
    "leap_attack",
}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a spotted leaper pelt"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    5969,
    5970,
    5971,
    5972,
    5973,
    5976,
    5977,
    5978,
    5979,
    5980,
    5981,
    5982,
    5983,
    5984
    }
Creature.roam_rooms = {
    5969,
    5970,
    5971,
    5972,
    5973,
    5976,
    5977,
    5978,
    5979,
    5980,
    5981,
    5982,
    5983,
    5984,
    5985,
    5986,
    5987
    }

Creature.roam_chance     = 30
Creature.respawn_seconds = 200
Creature.max_count       = 2

Creature.description = "Hind legs built for explosive power and spotted amber fur for camouflage in dappled light make the spotted leaper a dangerous ambush predator.  It crouches low against the ground, seemingly still, until some trigger releases it in a burst of speed and violence.  The impact of its full-body pounce is genuinely jarring."

return Creature
