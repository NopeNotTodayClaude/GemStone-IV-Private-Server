-- Creature: young grass snake
-- Zone: Rambling Meadows  |  Level: 1
local Creature = {}

Creature.id              = 9101
Creature.name            = "young grass snake"
Creature.level           = 1
Creature.family          = "snake"
Creature.classification  = "living"
Creature.body_type       = "ophidian"

Creature.hp_base         = 28
Creature.hp_variance     = 4

Creature.ds_melee        = 22
Creature.ds_bolt         = 8
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 3
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type="bite", as=18, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {
    "mild_venom",
}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a grass snake skin"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    5956,
    5957,
    5958,
    5959,
    5960,
    5961,
    5962
}
Creature.roam_rooms = {
    5956,
    5957,
    5958,
    5959,
    5960,
    5961,
    5962,
    5963,
    5964,
    6010
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 150
Creature.max_count       = 1

Creature.description = "Slender and dull-green with faint darker banding, this young grass snake moves in the characteristic S-curve of its kind.  It is barely longer than a forearm, and its flat head flicks a forked tongue to taste the air as it assesses whether you are a threat or a meal."

return Creature
