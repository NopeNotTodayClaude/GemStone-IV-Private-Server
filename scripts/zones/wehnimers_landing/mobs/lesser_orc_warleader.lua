-- Creature: lesser orc warleader
-- Zone: Wehnimer's Landing / Upper Trollfang  |  Level: 10
local Creature = {}

Creature.id              = 9404
Creature.name            = "lesser orc warleader"
Creature.level           = 10
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 138
Creature.hp_variance     = 12
Creature.ds_melee        = 98
Creature.ds_bolt         = 40
Creature.td_spiritual    = 28
Creature.td_elemental    = 28
Creature.udf             = 0
Creature.armor_asg       = 8
Creature.armor_natural   = false

Creature.attacks = {
    { type = "broadsword", as = 136, damage_type = "slash" },
    { type = "morning_star", as = 132, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = { "battle_fury", "shield_bash", "pack_tactics", "intimidating_presence" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "an orc ear"
Creature.special_loot = { "a warleader badge" }

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    452, 453, 454, 455, 456, 457, 458, 459,
    460, 461, 462, 463, 464, 465, 466, 467,
    468, 469, 470, 471, 472, 473, 474, 475,
    1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203
}

Creature.roam_rooms = {
    452, 453, 454, 455, 456, 457, 458, 459,
    460, 461, 462, 463, 464, 465, 466, 467,
    468, 469, 470, 471, 472, 473, 474, 475,
    1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203,
    1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211,
    1212, 1213, 1214, 1215, 1216
}

Creature.roam_chance     = 18
Creature.respawn_seconds = 360
Creature.max_count       = 1

Creature.description = "Bigger, louder, and far more organized than the orcs around it, the lesser orc warleader has plated together the spoils of older raids into a serviceable command harness.  It watches the field with a predator's patience, barking crude orders and smashing any underling that hesitates."

return Creature
