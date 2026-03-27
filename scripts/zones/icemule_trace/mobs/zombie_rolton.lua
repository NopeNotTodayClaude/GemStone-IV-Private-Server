-- Creature: zombie rolton
-- Zone: icemule_trace / Snowy Forest (Icemule Environs)  |  Level: 1
-- Source: https://gswiki.play.net/Zombie_rolton
-- HP: 28 | AS: 32 (bite+claw) | DS: 7 | bolt DS: 5 | UDF: 22 | TD: 3
-- ASG: 1N (natural) | Classification: corporeal undead
-- Treasure: no coins, no gems, no magic, no boxes. Skin: a rotting rolton pelt
local Creature = {}

Creature.id              = 10319
Creature.name            = "zombie rolton"
Creature.level           = 1
Creature.family          = "caprine"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "quadruped"

Creature.hp_base         = 28
Creature.hp_variance     = 4

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: bite 32 AS, claw 32 AS, DS 7, bolt DS 5, UDF 22, TD 3 all schools
Creature.ds_melee        = 7
Creature.ds_bolt         = 5
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 22
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 32, damage_type = "puncture" },
    { type = "claw", as = 32, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = {}

-- Undead immunities (standard corporeal undead)
Creature.immune = {
    "disease",
    "poison",
}

Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: no coins, no gems, no magic, no boxes. Skin: a rotting rolton pelt
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a rotting rolton pelt"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Icemule Snowy Forest entry area — shares the level-1 zone with rolton and
-- kobold. Roam boundary hard-capped here; will not drift into glatoph.
Creature.spawn_rooms = {
    3195, 3196, 3197, 3198,
    3199, 3200, 3201, 3202,
    3203, 3204, 3205, 3206,
}

Creature.roam_rooms = {
    3195, 3196, 3197, 3198,
    3199, 3200, 3201, 3202,
    3203, 3204, 3205, 3206,
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 180
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "An undead version of the domesticated breed, these were one of the earlier attempts by the Council of Twelve to create undead.  The zombie rolton's dirty, matted pelt hangs loosely from a bloated carcass, and its long, curved incisors gnash with mindless aggression.  It litters the snowy countryside and viciously attacks any living thing it sees."

return Creature
