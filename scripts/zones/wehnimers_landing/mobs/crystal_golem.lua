-- Creature: crystal golem
-- Zone: wehnimers_landing / Old Mine Road (rooms 4196, 2261-2282)  |  Level: 12
-- Source: https://gswiki.play.net/Crystal_golem
-- HP: 140 | AS: ensnare/pound 134 / stomp 144 | DS: 112 | bolt: 60 | TD: 36
-- ASG: 14N (double chain natural) | Body: biped | Classification: magical
-- Special: stomp foot quake effect | can_maneuver = 1
-- Treasure: coins yes, gems yes, magic yes, boxes yes | Skin: a crystal golem shard
local Creature = {}

Creature.id              = 9339
Creature.name            = "crystal golem"
Creature.level           = 12
Creature.family          = "golem"
Creature.classification  = "magical"
Creature.body_type       = "biped"

Creature.hp_base         = 140
Creature.hp_variance     = 14

Creature.ds_melee        = 112
Creature.ds_bolt         = 60
Creature.td_spiritual    = 36
Creature.td_elemental    = 36
Creature.udf             = 0
Creature.armor_asg       = 14
Creature.armor_natural   = true

Creature.attacks = {
    { type = "ensnare", as = 134, damage_type = "crush" },
    { type = "pound",   as = 134, damage_type = "crush" },
    { type = "stomp",   as = 144, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = { "stomp_quake", "golem_reconstruct" }
Creature.immune    = { "disease", "poison", "fear" }
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a crystal golem shard"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = ""

Creature.spawn_rooms = {
    2273, 2274, 2275, 2276, 2277,
    2278, 2279, 2280, 2281, 2282,
}

Creature.roam_rooms = {
    2273, 2274, 2275, 2276, 2277,
    2278, 2279, 2280, 2281, 2282,
}

Creature.roam_chance     = 10
Creature.respawn_seconds = 320
Creature.max_count       = 3

Creature.description = "The crystal golem was created to guard the mine and has been performing this function without interruption for longer than the mine has been worked. Its double-chain natural armour is not iron but compressed crystal lattice — it catches the light of the mine's torches and shatters it into cold fragments across the tunnel walls. When its foot comes down with full force, the tremor travels through the stone for twenty feet in every direction."

return Creature
