-- Creature: monkey
-- Zone: muddy_village / Muddy Village  |  Level: 6
-- Source: gswiki.play.net/Monkey
local Creature = {}

Creature.id              = 10421
Creature.name            = "monkey"
Creature.level           = 6
Creature.family          = "primate"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 60
Creature.hp_variance     = 6

Creature.ds_melee        = 48
Creature.ds_bolt         = 30
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 80
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "punch", as = 88, damage_type = "crush" },
    { type = "bite", as = 78, damage_type = "puncture" },
    { type = "club", as = 70, damage_type = "crush" },
}

Creature.spells = {}
Creature.abilities = { "hide", "taunt" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a monkey paw"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    29047, 29049, 29059, 29060, 29063, 29065, 29066, 29068, 29072, 29074,
    29075, 29076
}

Creature.roam_rooms = {
    29047, 29049, 29059, 29060, 29063, 29065, 29066, 29068, 29072, 29074,
    29075, 29076
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 200
Creature.max_count       = 7

Creature.description = "The monkey is barely two feet tall and completely convinced this gives it an advantage. It prowls the muddy lanes and huts of the village with erratic, unpredictable speed, striking with a scavenged club before vanishing behind piles of refuse and woven walls."

return Creature
