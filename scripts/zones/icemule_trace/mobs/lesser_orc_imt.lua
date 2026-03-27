-- Creature: lesser orc
-- Zone: Icemule Trace / Upper Trollfang Foothills  |  Level: 6
local Creature = {}

Creature.id              = 10326
Creature.name            = "lesser orc"
Creature.level           = 6
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 90
Creature.hp_variance     = 8

Creature.ds_melee        = 64
Creature.ds_bolt         = 30
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 0
Creature.armor_asg       = 7
Creature.armor_natural   = false

Creature.attacks = {
    { type="handaxe", as=88, damage_type="slash" },
    { type="shortsword", as=84, damage_type="slash" },
}

Creature.spells = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "an orc ear"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    2572, 2573, 2574, 2575, 2576, 2577, 2578
}

Creature.roam_rooms = {
    2572, 2573, 2574, 2575, 2576, 2577, 2578,
    2569, 2570, 2571
}

Creature.roam_chance     = 22
Creature.respawn_seconds = 240
Creature.max_count       = 2

Creature.description = "Wrapped in scavenged furs and rust-stained armor, the lesser orc prowls the foothills below Glatoph looking for easier prey than the things higher up the mountain.  Its confidence improves dramatically whenever it has friends nearby."

return Creature
