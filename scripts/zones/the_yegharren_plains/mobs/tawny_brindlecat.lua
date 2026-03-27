-- Creature: tawny brindlecat
-- Zone: the_yegharren_plains / Yegharren Plains  |  Level: 13
-- Source: https://gswiki.play.net/Tawny_brindlecat
-- HP: 120 | AS: claw 162 / bite 150 | DS: 97 (mid 71-124) | bolt: 45 | TD: 39
-- ASG: 8 (double leather natural) | Body: quadruped | Classification: living
-- Special: pounce maneuver | Treasure: no coins | Skin: a brindlecat pelt
local Creature = {}

Creature.id              = 10443
Creature.name            = "tawny brindlecat"
Creature.level           = 13
Creature.family          = "feline"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 120
Creature.hp_variance     = 12

Creature.ds_melee        = 97
Creature.ds_bolt         = 45
Creature.td_spiritual    = 39
Creature.td_elemental    = 39
Creature.udf             = 0
Creature.armor_asg       = 8
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 162, damage_type = "slash" },
    { type = "bite", as = 150, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = { "pounce_maneuver" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a brindlecat pelt"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    4990, 4991, 4992, 4993, 4994,
    4995, 4996, 4997, 4998, 4999,
    5000, 5001, 5002, 5003, 5004,
    5005, 5006, 5007, 5008, 5009,
}

Creature.roam_rooms = {
    4990, 4991, 4992, 4993, 4994,
    4995, 4996, 4997, 4998, 4999,
    5000, 5001, 5002, 5003, 5004,
    5005, 5006, 5007, 5008, 5009,
    5010, 5011, 5012, 5013, 5014,
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 260
Creature.max_count       = 6

Creature.description = "The tawny brindlecat moves through the high grass of the Yegharren Plains with the unhurried patience of a predator that knows nothing in this terrain is faster than it is. Its coat is a deep tawny gold broken by irregular dark brindle stripes that function as near-perfect camouflage in the dry grass. The pounce it delivers from concealment is the first indication most prey gets that the cat was ever there."

return Creature
