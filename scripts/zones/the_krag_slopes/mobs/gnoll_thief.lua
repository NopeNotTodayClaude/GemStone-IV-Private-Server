-- Creature: gnoll thief
-- Zone: the_krag_slopes / Krag Slopes (Zeltoph area)  |  Level: 13
-- Source: https://gswiki.play.net/Gnoll_thief
-- HP: 160 | AS: short sword 162 | DS: 176 | bolt: 90 (mid 72-109) | UDF: 0 | TD: 39
-- ASG: 6 (full leather) | Body: biped | Classification: living
-- Special: hurl weapon ability, steal item | Treasure: coins yes, boxes yes | Skin: a gnoll claw
local Creature = {}

Creature.id              = 10442
Creature.name            = "gnoll thief"
Creature.level           = 13
Creature.family          = "gnoll"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 160
Creature.hp_variance     = 16

Creature.ds_melee        = 176
Creature.ds_bolt         = 90
Creature.td_spiritual    = 39
Creature.td_elemental    = 39
Creature.udf             = 0
Creature.armor_asg       = 6
Creature.armor_natural   = false

Creature.attacks = {
    { type = "short_sword", as = 162, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = { "hurl_weapon", "steal_item" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a gnoll claw"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    6134, 6135, 6136, 6137, 6138,
    6139, 6140, 6141, 6142, 6143,
    6144, 6145, 6146, 6147, 6148,
    6149, 6150, 6151, 6152, 6153,
}

Creature.roam_rooms = {
    6134, 6135, 6136, 6137, 6138,
    6139, 6140, 6141, 6142, 6143,
    6144, 6145, 6146, 6147, 6148,
    6149, 6150, 6151, 6152, 6153,
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 280
Creature.max_count       = 6

Creature.description = "The gnoll thief operates by a simple philosophy: take everything that can be taken and hurl what cannot. Its defensive skill is genuinely exceptional for something wearing full leather — it moves with the fluid evasion of a creature that has spent years developing the specific art of not being where the weapon arrives. The short sword it wields is a backup. The thrown weapon that precedes it is the opening."

return Creature
