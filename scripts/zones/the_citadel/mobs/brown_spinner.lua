-- brown spinner L9 | the_citadel / River Tunnels deep | ID 10433
local Creature = {}

Creature.id              = 10433
Creature.name            = "brown spinner"
Creature.level           = 9
Creature.family          = "arachnid"
Creature.classification  = "living"
Creature.body_type       = "arachnid"

Creature.hp_base         = 90
Creature.hp_variance     = 9

Creature.ds_melee        = 115
Creature.ds_bolt         = 60
Creature.td_spiritual    = 27
Creature.td_elemental    = 27
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 113, damage_type = "slash" },
}

Creature.spells = {

}
Creature.abilities = { "web_immobilize" }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a brown spinner leg"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    11196, 11197, 11198, 11199, 11200, 11201, 11202, 11203, 11204, 11205, 11206, 11207, 11208, 11209, 11210
}

Creature.roam_rooms = {
    11196, 11197, 11198, 11199, 11200, 11201, 11202, 11203, 11204, 11205, 11206, 11207, 11208, 11209, 11210
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 4

Creature.description = "The brown spinner builds webs across the tunnel junctions and waits in them rather than above them — a flat, patient shape indistinguishable from the silk until it moves. Its defensive speed is remarkable; approaches that would work against the albino tomb spider do not work here, and it knows this. The web it throws is projectile and fast."

return Creature
