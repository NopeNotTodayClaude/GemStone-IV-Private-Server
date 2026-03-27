-- Creature: spotted velnalin
-- Zone: yanders_farm / Yander's Farm  |  Level: 3
-- Source: GUESSED - balanced vs velnalin L3 (71 AS, 32 DS)
-- HP: 48 | AS: charge 72 AS / bite 55 AS (guessed) | DS: 36 | bolt DS: 15 | TD: 9
-- ASG: 5N (natural) | Body: quadruped
-- Treasure: no coins | Skin: a velnalin horn
local Creature = {}

Creature.id              = 10417
Creature.name            = "spotted velnalin"
Creature.level           = 3
Creature.family          = "deer"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 48
Creature.hp_variance     = 4

Creature.ds_melee        = 36
Creature.ds_bolt         = 15
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 75
Creature.armor_asg       = 5
Creature.armor_natural   = true

Creature.attacks = {
    { type = "charge", as = 72, damage_type = "crush" },
    { type = "bite", as = 55, damage_type = "puncture" },
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
Creature.skin         = "a velnalin horn"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    6012, 6013, 6014, 6016, 6018, 6019, 6020, 6021, 6022, 6023, 6025, 6026
}
Creature.roam_rooms  = {
    6012, 6013, 6014, 6015, 6016, 6017, 6018, 6019, 6020, 6021, 6022, 6023, 6024, 6025, 6026
}
Creature.roam_chance     = 20
Creature.respawn_seconds = 180
Creature.max_count       = 2

Creature.description = "The spotted velnalin moves through the farm's outer pastures with deceptive calm, its dappled coat shifting between gold and grey as it steps through the long grass. Like its striped kin it has the wrong teeth for a deer — sharp, interlocking, and clearly not for grazing. It watches you with patient dark eyes right up until the moment it decides not to."

return Creature
