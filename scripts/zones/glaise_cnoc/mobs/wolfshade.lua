-- Creature: wolfshade
-- Zone: glaise_cnoc  |  Level: 15
local Creature = {}

Creature.id              = 2004
Creature.name            = "wolfshade"
Creature.level           = 15
Creature.family          = "canine"
Creature.classification  = "non_corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "quadruped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 140
Creature.hp_variance     = 8

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 90
Creature.ds_bolt         = 68
Creature.td_spiritual    = 45
Creature.td_elemental    = 45
Creature.udf             = 110
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 133, damage_type = "puncture" },
    { type = "claw", as = 133, damage_type = "slash" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "non_corporeal",
    "pack_hunting",
}

Creature.immune = {
    "disease",
    "poison",
    "normal_weapon",
}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = ""
Creature.special_loot = {

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
}

Creature.roam_chance     = 30   -- % chance to move each tick
Creature.respawn_seconds = 360
Creature.max_count       = 6

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The wolfshade is the animated spirit of a powerful northern grey wolf.  Even in death it still possesses keen hearing, smell, sight, and extremely quick reflexes.  Dark grey with bloodshot eyes, it is driven onward by a hunger for living flesh it can never satisfy."

return Creature
