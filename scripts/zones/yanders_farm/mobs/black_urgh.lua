-- Creature: black urgh
-- Zone: yanders_farm / Yander's Farm  |  Level: 4
-- Source: GUESSED - balanced vs urgh L4 (Vornavian urgh wiki stats)
-- HP: 88 | AS: charge 80 AS / tusk 68 AS (guessed) | DS: 62 | bolt DS: 20 | TD: 12
-- ASG: 5N (natural) | Body: quadruped
-- Treasure: no coins | Skin: a black urgh hide
local Creature = {}

Creature.id              = 10418
Creature.name            = "black urgh"
Creature.level           = 4
Creature.family          = "suine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 88
Creature.hp_variance     = 8

Creature.ds_melee        = 62
Creature.ds_bolt         = 20
Creature.td_spiritual    = 12
Creature.td_elemental    = 12
Creature.udf             = 90
Creature.armor_asg       = 5
Creature.armor_natural   = true

Creature.attacks = {
    { type = "charge", as = 80, damage_type = "crush" },
    { type = "gore", as = 68, damage_type = "puncture" },
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
Creature.skin         = "a black urgh hide"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = { 5040, 5041, 5042, 5043, 5044, 5045, 5046, 5047, 5048, 5049, 5050, 5051, 5052, 5053, 5054, 5055, 5056, 5057, 5058, 5059 }
Creature.roam_rooms  = { 5040, 5041, 5042, 5043, 5044, 5045, 5046, 5047, 5048, 5049, 5050, 5051, 5052, 5053, 5054, 5055, 5056, 5057, 5058, 5059 }
Creature.roam_chance     = 20
Creature.respawn_seconds = 200
Creature.max_count       = 7

Creature.description = "The herbivorous black urgh resembles an overgrown, hairy pig standing on four feet with a dusty black coat and a curled, hairless tail. Instead of the usual upper and lower jaw in front of his head, the black urgh has an extremely long upper lip which he can extend a good two feet to drag vegetation back into his mouth. Under the mouth reside two long curved tusks he uses to root through earth — and, with no particular malice, to remove anyone standing between him and his next meal."

return Creature
