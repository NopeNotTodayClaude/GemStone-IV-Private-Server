-- Creature: thyril
-- Zone: Rambling Meadows  |  Level: 2
local Creature = {}

Creature.id              = 9105
Creature.name            = "thyril"
Creature.level           = 2
Creature.family          = "thyril"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 44
Creature.hp_variance     = 5

Creature.ds_melee        = 32
Creature.ds_bolt         = 14
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 3
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type="claw", as=36, damage_type="slash" },
    { type="bite", as=32, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {
    "evade_maneuver",
}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a thyril pelt"
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
    6010
    }

Creature.roam_chance     = 30
Creature.respawn_seconds = 160
Creature.max_count       = 1

Creature.description = "A young thyril, barely past cub stage, stalks through the tall grass with exaggerated caution.  Its spotted, tawny coat provides effective camouflage in the meadow, and its oversized paws hint at the larger predator it will become.  Even at this age, its reflexes are startlingly quick."

return Creature
