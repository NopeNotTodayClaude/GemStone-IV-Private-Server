-- Creature: coconut crab
-- Zone: rocky_shoals / Rocky Shoals  |  Level: 2
-- Source: GUESSED - balanced vs pale crab L2
-- HP: 45 | AS: claw 45 AS (guessed) | DS: 30 | bolt DS: 18 | TD: 6
-- ASG: 12N (natural) | Body: crustacean
-- Treasure: no coins | Skin: a coconut crab claw
local Creature = {}

Creature.id              = 10416
Creature.name            = "coconut crab"
Creature.level           = 2
Creature.family          = "crab"
Creature.classification  = "living"
Creature.body_type       = "crustacean"

Creature.hp_base         = 45
Creature.hp_variance     = 4

Creature.ds_melee        = 30
Creature.ds_bolt         = 18
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 35
Creature.armor_asg       = 12
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 45, damage_type = "crush" },
    { type = "pincer", as = 40, damage_type = "crush" },
}

Creature.spells = {

}
Creature.abilities = { "ensnare" }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a coconut crab claw"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = { 29188, 29189, 29190, 29191, 29192, 29193, 29194, 29195, 29196, 29197, 29198, 29199, 29200 }
Creature.roam_rooms  = { 29188, 29189, 29190, 29191, 29192, 29193, 29194, 29195, 29196, 29197, 29198, 29199, 29200 }
Creature.roam_chance     = 20
Creature.respawn_seconds = 180
Creature.max_count       = 8

Creature.description = "The coconut crab is far larger than any crab has a right to be, its shell patterned in rings of dull brown and cream that might look like carved wood from a distance. Its claws are absurdly oversized relative to its body and capable of exerting crushing force sufficient to split bone. It moves with a slow, deliberate patience that suggests it has never needed to hurry."

return Creature
