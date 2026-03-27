-- Creature: raider orc
-- Zone: Yander's Farm / Wheat & Barley Fields  |  Level: 10
local Creature = {}
Creature.id              = 9203
Creature.name            = "raider orc"
Creature.level           = 10
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 135
Creature.hp_variance     = 10
Creature.ds_melee        = 92
Creature.ds_bolt         = 44
Creature.td_spiritual    = 32
Creature.td_elemental    = 32
Creature.udf             = 0
Creature.armor_asg       = 9
Creature.armor_natural   = false
Creature.attacks = {
    { type="broadsword", as=142, damage_type="slash" },
    { type="handaxe", as=136, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "battle_fury",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "an orc ear"
Creature.special_loot = {
    "a crude orc token",
}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    6073,
    6074,
    6075,
    6076,
    6077,
    6078,
    6079,
    6080,
    6081,
    6082,
    6083,
    6084,
    6085,
    6086,
    6087,
    6088,
    6089,
    6060,
    6061,
    6062,
    6063,
    6064,
    6065,
    6066,
    6067,
    6068,
    6069,
    6070,
    6071,
    6072,
    10261
    }
Creature.roam_rooms = {
    6073,
    6074,
    6075,
    6076,
    6077,
    6078,
    6079,
    6080,
    6081,
    6082,
    6083,
    6084,
    6085,
    6086,
    6087,
    6088,
    6089,
    6060,
    6061,
    6062,
    6063,
    6064,
    6065,
    6066,
    6067,
    6068,
    6069,
    6070,
    6071,
    6072,
    10261,
    6024,
    6041,
    6042,
    6043,
    6044
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 4
Creature.description = "Well-equipped by orc standards, the raider orc wears looted armor with the straps adjusted to roughly fit its stocky frame.  A broad sword or heavy axe sits in each hand, and a wide belt strains to hold pouches of pilfered goods.  The raid-marks painted across its face mark it as a veteran of many excursions into settled lands."
return Creature
