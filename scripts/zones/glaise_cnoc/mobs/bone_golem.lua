-- Creature: bone golem
-- Zone: glaise_cnoc  |  Level: 8
local Creature = {}

Creature.id              = 2001
Creature.name            = "bone golem"
Creature.level           = 8
Creature.family          = "golem"
Creature.classification  = "corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 90
Creature.hp_variance     = 10

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 12
Creature.ds_bolt         = 2
Creature.td_spiritual    = 24
Creature.td_elemental    = 24
Creature.udf             = 0
Creature.armor_asg       = 12
Creature.armor_natural   = true

Creature.attacks = {
    { type = "ensnare", as = 97, damage_type = "crush" },
    { type = "pound", as = 107, damage_type = "crush" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "tail_sweep",
    "puncture_resistant",
    "holding_song_immune",
    "crystal_core_drop",
}

Creature.immune = {
    "disease",
    "poison",
}

Creature.resist = {
    "puncture",
}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a golem bone"
Creature.special_loot = {
    "crystal core",
}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10694,
    10695,
    10696,
    10697,
    10698,
    10699,
    10700,
    10701,
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
    10694,
    10695,
    10696,
    10697,
    10698,
    10699,
    10700,
    10701,
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

Creature.roam_chance     = 15   -- % chance to move each tick
Creature.respawn_seconds = 300
Creature.max_count       = 5

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Dried bones send sickening clacking sounds at the barest movement of the bone golem.  Its large skull is capped with twin horns of sharply spiraled bone, with a long spine ending in a sharp tail that whips back and forth in a vicious swipe."

return Creature
