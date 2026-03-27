-- Creature: shadowy spectre
-- Zone: glaise_cnoc  |  Level: 14
local Creature = {}

Creature.id              = 2003
Creature.name            = "shadowy spectre"
Creature.level           = 14
Creature.family          = "ghost"
Creature.classification  = "non_corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 130
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 135
Creature.ds_bolt         = 64
Creature.td_spiritual    = 42
Creature.td_elemental    = 42
Creature.udf             = 161
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 106, damage_type = "slash" },
    { type = "closed_fist", as = 105, damage_type = "crush" },
    { type = "pound", as = 92, damage_type = "crush" },
}

Creature.spells = {
    { name = "Major Cold", cs = 0, as = 137 },
    { name = "Minor Shock", cs = 0, as = 137 },
    { name = "Repel (Fear)", cs = 94, as = 0 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "non_corporeal",
    "cold_flare",
    "call_wind",
    "gas_cloud",
    "drops_pale_water_sapphire",
}

Creature.immune = {
    "disease",
    "poison",
    "normal_weapon",
}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = ""
Creature.special_loot = {
    "pale water sapphire",
}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10702,
    10703,
    10704,
    10705,
    10706,
    10707,
    10708,
    10709,
    10710,
    10711,
    10712,
    10713,
    10714,
    10715,
    10716,
    10717,
    10718,
    10719,
    10720,
    10721,
    10722,
    10723,
    10724,
    10725,
    10726,
    10727,
    10728,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10702,
    10703,
    10704,
    10705,
    10706,
    10707,
    10708,
    10709,
    10710,
    10711,
    10712,
    10713,
    10714,
    10715,
    10716,
    10717,
    10718,
    10719,
    10720,
    10721,
    10722,
    10723,
    10724,
    10725,
    10726,
    10727,
    10728,
}

Creature.roam_chance     = 25   -- % chance to move each tick
Creature.respawn_seconds = 360
Creature.max_count       = 4

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The shadowy spectre, a flickering shadowy apparition, floats inches above the ground, seeming to move through solid obstacles.  Possessed of excellent incantation ability, it prefers magical combat.  Its shadowy shape flickers in and out of reality."

return Creature
