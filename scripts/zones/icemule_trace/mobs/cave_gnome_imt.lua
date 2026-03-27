-- Creature: cave gnome
-- Zone: Icemule Trace / Snowflake Vale Clearings  |  Level: 2
local Creature = {}

Creature.id              = 10324
Creature.name            = "cave gnome"
Creature.level           = 2
Creature.family          = "gnome"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 42
Creature.hp_variance     = 5

Creature.ds_melee        = 26
Creature.ds_bolt         = 12
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 2
Creature.armor_natural   = false

Creature.attacks = {
    { type="dagger", as=38, damage_type="puncture" },
    { type="thrown_rock", as=32, damage_type="crush" },
}

Creature.spells = {}
Creature.abilities = {
    "cave_sight",
    "hide_in_shadows",
}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = true
Creature.skin        = "a gnome ear"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214
}

Creature.roam_rooms = {
    3203, 3204, 3205, 3206,
    3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 170
Creature.max_count       = 2

Creature.description = "Pallid, quick-fingered, and badly dressed for the cold, the cave gnome darts from snow-choked hollows and brush piles with a scavenger's nerve.  It carries stolen odds and ends in a patched satchel and looks perpetually offended to find anyone else in its chosen territory."

return Creature
