-- crocodile L9 | the_citadel / River Tunnels (flooded sections) + marshtown | ID 10434
local Creature = {}

Creature.id              = 10434
Creature.name            = "crocodile"
Creature.level           = 9
Creature.family          = "reptilian"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 90
Creature.hp_variance     = 9

Creature.ds_melee        = 75
Creature.ds_bolt         = 40
Creature.td_spiritual    = 27
Creature.td_elemental    = 27
Creature.udf             = 0
Creature.armor_asg       = 16
Creature.armor_natural   = true

Creature.attacks = {
    { type = "charge", as = 137, damage_type = "crush" },
}

Creature.spells = {

}
Creature.abilities = { "disease_on_hit" }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a crocodile hide"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    11211, 11212, 11213, 11214, 11215, 11216, 11217, 11218, 11219, 11220, 11221, 11222, 11223, 11224, 11225
}

Creature.roam_rooms = {
    11211, 11212, 11213, 11214, 11215, 11216, 11217, 11218, 11219, 11220, 11221, 11222, 11223, 11224, 11225
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 300
Creature.max_count       = 3

Creature.description = "The crocodile has been here long enough that the tunnel-dwelling variety has lost nothing of the surface version except sunlight. It lies still in the flooded passages with its back just below the waterline, indistinguishable from a log or a shelf of stone until the charge. The chain hauberk of its natural armour makes it nearly impervious to anything short of sustained assault."

return Creature
