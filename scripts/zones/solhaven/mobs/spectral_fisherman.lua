-- Creature: spectral fisherman
-- Zone: solhaven / Coastal Cliffs (Vornavian Coast)  |  Level: 6
-- Source: gswiki.play.net/Spectral_fisherman
-- HP: 90 | AS: trident 94 AS | DS: 15 | bolt DS: 7 | TD: 18
-- ASG: 1N | Body: biped
-- Treasure: coins+boxes | Skin: 
local Creature = {}
Creature.id              = 10423
Creature.name            = "spectral fisherman"
Creature.level           = 6
Creature.family          = "ghost"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 90
Creature.hp_variance     = 9
Creature.ds_melee        = 15
Creature.ds_bolt         = 7
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true
Creature.attacks = {
    { type = "trident", as = 94, damage_type = "puncture" },
}
Creature.spells = {

}
Creature.abilities = {  }
Creature.immune    = { "poison", "disease", "slash", "puncture", "crush" }
Creature.resist    = {}
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = ""
Creature.special_loot = {}
Creature.decay_seconds = 60
Creature.crumbles      = true
Creature.decay_message = ""
Creature.spawn_rooms = { 7673, 7674, 7675, 7676, 7677, 7678, 7679, 7680, 7681, 7601 }
Creature.roam_rooms  = { 7673, 7674, 7675, 7676, 7677, 7678, 7679, 7680, 7681, 7601 }
Creature.roam_chance     = 20
Creature.respawn_seconds = 240
Creature.max_count       = 5
Creature.description = "The spectral fisherman still stands as it did in life — bent slightly at the knee, weight forward, arm raised with a trident of cold spectral light. It has no memory of its name, its catch, or its crew. It has only the motion, repeated endlessly: the cast, the haul, the strike. If you stand in the way of that motion it will not stop."
return Creature
