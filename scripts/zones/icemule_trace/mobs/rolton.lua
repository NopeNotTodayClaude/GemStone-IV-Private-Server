-- Creature: rolton
-- Zone: Icemule Trace / Snowy Forest  |  Level: 1
local Creature = {}
Creature.id              = 10301
Creature.name            = "rolton"
Creature.level           = 1
Creature.family          = "rolton"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 30
Creature.hp_variance     = 3
Creature.ds_melee        = 20
Creature.ds_bolt         = 5
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="headbutt", as=18, damage_type="crush" },
    { type="bite", as=14, damage_type="puncture" },
}
Creature.spells          = {}
Creature.abilities       = {}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a rolton fleece"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    3195,
    3196,
    3197,
    3198,
    3199,
    3200,
    3201,
    3202
    }
Creature.roam_rooms      = {
    3195,
    3196,
    3197,
    3198,
    3199,
    3200,
    3201,
    3202
    }
Creature.roam_chance     = 35
Creature.respawn_seconds = 150
Creature.max_count       = 1
Creature.description     = "A sturdy cold-weather rolton, its thick wool coat matted with snow and frozen mud.  The amber eyes with rectangular pupils assess you with the same bold hostility as its warmer-climate cousins, and the horns on the male have the look of weapons that have been used as weapons."
return Creature
