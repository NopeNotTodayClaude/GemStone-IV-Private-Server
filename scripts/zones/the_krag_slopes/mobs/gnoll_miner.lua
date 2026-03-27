-- gnoll miner L10 | the_krag_slopes / Krag Slopes (Zeltoph area) | ID 10437
local Creature = {}

Creature.id              = 10437
Creature.name            = "gnoll miner"
Creature.level           = 10
Creature.family          = "gnoll"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 105
Creature.hp_variance     = 10

Creature.ds_melee        = 84
Creature.ds_bolt         = 50
Creature.td_spiritual    = 30
Creature.td_elemental    = 30
Creature.udf             = 100
Creature.armor_asg       = 8
Creature.armor_natural   = false

Creature.attacks = {
    { type = "handaxe", as = 125, damage_type = "slash" },
}

Creature.spells = {

}
Creature.abilities = {  }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a gnoll tooth"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    6119, 6120, 6121, 6122, 6123, 6124, 6125, 6126, 6127, 6128, 6129, 6130, 6131, 6132, 6133
}

Creature.roam_rooms = {
    6119, 6120, 6121, 6122, 6123, 6124, 6125, 6126, 6127, 6128, 6129, 6130, 6131, 6132, 6133
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 5

Creature.description = "The gnoll miner swings a handaxe with the efficiency of something that has spent its working life bringing it down onto stone. The mining background has given it exceptional upper body strength and a complete indifference to dust, confined spaces, and the sound of things collapsing nearby. It does not roar or posture before attacking — it just swings."

return Creature
