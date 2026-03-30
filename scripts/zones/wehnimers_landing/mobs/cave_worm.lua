-- cave worm L10 | wehnimers_landing / Mine Road + Old Mine (rooms 4196, 2261-2282) | ID 9338
local Creature = {}

Creature.id              = 9338
Creature.name            = "cave worm"
Creature.level           = 10
Creature.family          = "worm"
Creature.classification  = "living"
Creature.body_type       = "worm"

Creature.hp_base         = 100
Creature.hp_variance     = 10

Creature.ds_melee        = 118
Creature.ds_bolt         = 58
Creature.td_spiritual    = 30
Creature.td_elemental    = 30
Creature.udf             = 0
Creature.armor_asg       = 12
Creature.armor_natural   = true

Creature.attacks = {
    { type = "ensnare", as = 139, damage_type = "crush" },
}

Creature.spells = {

}
Creature.abilities = {  }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a cave worm hide"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    2267, 2268, 2269, 2270, 2271, 2272, 2273, 2274, 2275, 2276, 2277, 2278
}

Creature.roam_rooms = {
    2267, 2268, 2269, 2270, 2271, 2272, 2273, 2274, 2275, 2276, 2277, 2278
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 300
Creature.max_count       = 3

Creature.description = "The cave worm erupts from the soft earth of the mine floor with no warning, displacing rock and timber with equal indifference. Its ensnare coils quickly and holds with muscular, mechanical force while its bite handles the rest. The brigandine-grade natural armour of its outer hide means that standard weapons have to find the right angle, and the worm is never still long enough to make that easy."

return Creature
