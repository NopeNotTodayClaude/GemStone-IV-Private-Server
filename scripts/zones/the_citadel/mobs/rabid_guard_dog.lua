-- rabid guard dog L10 | the_citadel / River Tunnels guard stations | ID 10438
local Creature = {}

Creature.id              = 10438
Creature.name            = "rabid guard dog"
Creature.level           = 10
Creature.family          = "canine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 100
Creature.hp_variance     = 10

Creature.ds_melee        = 77
Creature.ds_bolt         = 37
Creature.td_spiritual    = 30
Creature.td_elemental    = 30
Creature.udf             = 85
Creature.armor_asg       = 6
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 123, damage_type = "puncture" },
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
Creature.skin         = "a guard dog pelt"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    11226, 11227, 11228, 11229, 11230, 11231, 11232, 11233, 11234, 11235, 11236, 11237, 11238, 11239, 11240
}

Creature.roam_rooms = {
    11226, 11227, 11228, 11229, 11230, 11231, 11232, 11233, 11234, 11235, 11236, 11237, 11238, 11239, 11240
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 4

Creature.description = "The rabid guard dog was bred for this work and then left here long enough to go wrong. It is large, heavily built, and moves with the locked-jaw focus of an animal that has forgotten most things except the directive to stop anything that enters this section of tunnel. The disease it carries has progressed to the point where it is visibly affecting its movement — which makes it faster, not slower."

return Creature
