-- albino tomb spider L8 | wehnimers_landing / The Graveyard | ID 9337
local Creature = {}

Creature.id              = 9337
Creature.name            = "albino tomb spider"
Creature.level           = 8
Creature.family          = "arachnid"
Creature.classification  = "living"
Creature.body_type       = "arachnid"

Creature.hp_base         = 83
Creature.hp_variance     = 8

Creature.ds_melee        = 77
Creature.ds_bolt         = 52
Creature.td_spiritual    = 24
Creature.td_elemental    = 24
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 116, damage_type = "slash" },
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
Creature.skin         = "a tomb spider leg"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    7163, 7164, 7165, 7166, 7167, 7168, 7169, 7170, 7171, 7172, 7200, 7201, 7202, 7203, 7204, 7205, 7206, 7207, 7208, 7209, 7210
}

Creature.roam_rooms = {
    7163, 7164, 7165, 7166, 7167, 7168, 7169, 7170, 7171, 7172, 7200, 7201, 7202, 7203, 7204, 7205, 7206, 7207, 7208, 7209, 7210
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 260
Creature.max_count       = 5

Creature.description = "The albino tomb spider has spent so many generations in lightless crypts that colour has left it entirely. Its body is chalk-white, almost luminescent in darkness, and the silk it produces is not the usual sticky amber but something that looks like frost and holds just as fast. It is patient in the way that only things which do not need to eat often can afford to be."

return Creature
