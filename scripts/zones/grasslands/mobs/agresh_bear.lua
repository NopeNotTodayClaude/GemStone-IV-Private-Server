-- Creature: Agresh bear
-- Zone: Grasslands / Apple Orchard  |  Level: 16
local Creature = {}

Creature.id              = 9004
Creature.name            = "Agresh bear"
Creature.level           = 16
Creature.family          = "bear"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 196
Creature.hp_variance     = 15

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 138
Creature.ds_bolt         = 58
Creature.td_spiritual    = 51
Creature.td_elemental    = 51
Creature.udf             = 4
Creature.armor_asg       = 7
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 186, damage_type = "slash" },
    { type = "bite", as = 180, damage_type = "puncture" },
    { type = "bear_hug", as = 178, damage_type = "crush" },
}

Creature.spells = {}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "bear_maul",
    "toughskin",
}

Creature.immune = {}

Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "an Agresh bear pelt"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
Creature.spawn_rooms = {
    10216,
    10217,
    10218,
    10219,
    10220,
    10221,
    10222,
    10223,
    10224,
    10225,
    10226,
    10227,
    10228,
    10229,
    10230,
    10231,
    10232,
    10253,
    10254,
    10255,
    10256,
    10257,
    10258,
    10259,
    10260
}

Creature.roam_rooms = {
    10216,
    10217,
    10218,
    10219,
    10220,
    10221,
    10222,
    10223,
    10224,
    10225,
    10226,
    10227,
    10228,
    10229,
    10230,
    10231,
    10232,
    10253,
    10254,
    10255,
    10256,
    10257,
    10258,
    10259,
    10260,
    10171,
    10172,
    10173,
    10174
}

Creature.roam_chance     = 15
Creature.respawn_seconds = 360
Creature.max_count       = 3

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Broader across the shoulders than most horses are long, the Agresh bear rears up to display impressive height before dropping back to all fours with a ground-shaking thud.  Its thick, dark pelt is matted with old scars and new mud, and the curved claws on each paw could strip bark from an oak tree without effort."

return Creature
