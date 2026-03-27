-- Creature: blood eagle  |  Zone: the_citadel / River Tunnels upper  |  Level: 7
-- Source: gswiki.play.net/Blood_eagle
-- HP: 120 | AS: claw 100+ AS, carry-and-drop | DS: 38 | bolt: 17 | TD: 21 | ASG: 1N
local Creature = {}

Creature.id              = 10424
Creature.name            = "blood eagle"
Creature.level           = 7
Creature.family          = "bird"
Creature.classification  = "living"
Creature.body_type       = "avian"

Creature.hp_base         = 120
Creature.hp_variance     = 12

Creature.ds_melee        = 38
Creature.ds_bolt         = 17
Creature.td_spiritual    = 21
Creature.td_elemental    = 21
Creature.udf             = 50
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {

}

Creature.spells = {

}
Creature.abilities = { "carry_and_drop" }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a blood eagle feather"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    11166, 11167, 11168, 11169, 11170, 11171, 11172, 11173, 11174, 11175, 11176, 11177, 11178, 11179, 11180
}

Creature.roam_rooms = {
    11166, 11167, 11168, 11169, 11170, 11171, 11172, 11173, 11174, 11175, 11176, 11177, 11178, 11179, 11180
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 260
Creature.max_count       = 4

Creature.description = "The blood eagle's wingspan is wide enough to block a corridor when fully extended, and it uses this fact deliberately — landing in a doorway, spreading its wings, and forcing a choice. The scarlet wash across its breast feathers is not plumage; it is accumulation. Its talons are built for carrying prey aloft and releasing it from height, which it demonstrates with a patience that makes the approach to its nesting ground a lesson in attention."

return Creature
