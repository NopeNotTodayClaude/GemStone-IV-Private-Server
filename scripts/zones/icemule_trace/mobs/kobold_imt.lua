-- Creature: kobold
-- Zone: Icemule Trace / Snowy Forest  |  Level: 1
local Creature = {}
Creature.id              = 10302
Creature.name            = "kobold"
Creature.level           = 1
Creature.family          = "kobold"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 24
Creature.hp_variance     = 3
Creature.ds_melee        = 22
Creature.ds_bolt         = 8
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 2
Creature.armor_natural   = false
Creature.attacks         = {
    { type="dagger", as=22, damage_type="puncture" },
    { type="handaxe", as=18, damage_type="slash" },
}
Creature.spells          = {}
Creature.abilities       = {}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = false
Creature.loot_boxes      = true
Creature.skin            = "a kobold skin"
Creature.special_loot    = {
    "a kobold ear",
}
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
    3202,
    3203,
    3204,
    3205,
    3206
    }
Creature.roam_rooms      = {
    3195,
    3196,
    3197,
    3198,
    3199,
    3200,
    3201,
    3202,
    3203,
    3204,
    3205,
    3206
    }
Creature.roam_chance     = 30
Creature.respawn_seconds = 150
Creature.max_count       = 1
Creature.description     = "The Icemule kobold has adapted to cold with a coat of coarser, denser scales over its natural skin.  Otherwise it is identical to its warmer-climate kin — scavenging, mischievous, and willing to attack anything it outnumbers sufficiently.  The cold has not improved its temperament."
return Creature
