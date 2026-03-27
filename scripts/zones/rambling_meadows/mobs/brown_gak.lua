-- Creature: brown gak
-- Zone: Rambling Meadows  |  Level: 2
local Creature = {}

Creature.id              = 9104
Creature.name            = "brown gak"
Creature.level           = 2
Creature.family          = "gak"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 42
Creature.hp_variance     = 5

Creature.ds_melee        = 28
Creature.ds_bolt         = 12
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 2
Creature.armor_natural   = false

Creature.attacks = {
    { type="claw", as=38, damage_type="slash" },
    { type="bite", as=34, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a gak hide"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    5956,
    5957,
    5958,
    6010,
    5959,
    5960,
    5961,
    5962,
    5963,
    5964
    }
Creature.roam_rooms = {
    5956,
    5957,
    5958,
    6010,
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
    5973
    }

Creature.roam_chance     = 30
Creature.respawn_seconds = 160
Creature.max_count       = 2

Creature.description = "Squat, roughly man-shaped, and covered in coarse brown fur, the brown gak shuffles about on stubby legs with its knuckles occasionally brushing the ground.  Beady black eyes glitter beneath a heavy brow, and a wide lipless mouth shows rows of flat crushing teeth.  It smells powerfully of wet fur and rotting vegetation."

return Creature
