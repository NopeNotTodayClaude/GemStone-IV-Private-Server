-- Creature: black leopard
-- Zone: Grasslands / Foothills & Orchard  |  Level: 15
local Creature = {}

Creature.id              = 9003
Creature.name            = "black leopard"
Creature.level           = 15
Creature.family          = "feline"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 190
Creature.hp_variance     = 14

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 152
Creature.ds_bolt         = 70
Creature.td_spiritual    = 49
Creature.td_elemental    = 49
Creature.udf             = 6
Creature.armor_asg       = 2
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 182, damage_type = "slash" },
    { type = "bite", as = 175, damage_type = "puncture" },
    { type = "rake", as = 170, damage_type = "slash" },
}

Creature.spells = {}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "pounce_maneuver",
    "stealth_ambush",
}

Creature.immune = {}

Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a black leopard pelt"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
Creature.spawn_rooms = {
    10171,
    10172,
    10173,
    10174,
    10175,
    10176,
    10177,
    10178,
    10179,
    10180,
    10181,
    10182,
    10185,
    10186,
    10187,
    10188,
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
    10171,
    10172,
    10173,
    10174,
    10175,
    10176,
    10177,
    10178,
    10179,
    10180,
    10181,
    10182,
    10185,
    10186,
    10187,
    10188,
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

Creature.roam_chance     = 30
Creature.respawn_seconds = 300
Creature.max_count       = 6

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Sleek muscle beneath a coat of pure midnight black, the black leopard moves with fluid, absolute silence.  Its amber eyes are fixed and calculating as it pads through the terrain.  Even its breathe seems muffled — a predator designed by nature to be seen only when it chooses."

return Creature
