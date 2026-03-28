-- Creature: rogue hobgoblin marauder
-- Zone: Wehnimer's Landing / Upper Trollfang fringe  |  Level: 6
local Creature = {}

Creature.id              = 9323
Creature.name            = "rogue hobgoblin marauder"
Creature.level           = 6
Creature.family          = "goblin"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 92
Creature.hp_variance     = 8
Creature.ds_melee        = 66
Creature.ds_bolt         = 22
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 57
Creature.armor_asg       = 7
Creature.armor_natural   = false

Creature.attacks = {
    { type = "claidhmore", as = 96, damage_type = "slash" },
    { type = "handaxe",    as = 92, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = { "scavenge_weapon", "hobgoblin_antics", "battle_fury", "pack_tactics" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a hobgoblin scalp"
Creature.special_loot = { "a marauder token" }

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    452, 453, 454, 455, 456, 457, 458, 459,
    460, 461, 462, 463, 464, 465, 466, 467
}

Creature.roam_rooms = {
    452, 453, 454, 455, 456, 457, 458, 459,
    460, 461, 462, 463, 464, 465, 466, 467,
    468, 469, 470, 471, 472, 473, 474, 475
}

Creature.roam_chance     = 26
Creature.respawn_seconds = 300
Creature.max_count       = 1

Creature.description = "Scarred and self-important, the rogue hobgoblin marauder wears the best pieces stripped from lesser raiders and swings them around with theatrical cruelty.  A belt full of stolen trinkets rattles against its hip each time it lunges in for another opportunistic strike."

return Creature
