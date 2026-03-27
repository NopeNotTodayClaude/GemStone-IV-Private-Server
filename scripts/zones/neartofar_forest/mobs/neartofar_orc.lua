-- Creature: Neartofar orc
-- Zone: neartofar_forest  |  Level: 11
local Creature = {}

Creature.id              = 6002
Creature.name            = "Neartofar orc"
Creature.level           = 11
Creature.family          = "orc"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 140
Creature.hp_variance     = 12

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 80
Creature.ds_bolt         = 59
Creature.td_spiritual    = 32
Creature.td_elemental    = 32
Creature.udf             = 0
Creature.armor_asg       = 12
Creature.armor_natural   = false

Creature.attacks = {
    { type = "morning_star", as = 159, damage_type = "crush" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {

}

Creature.immune = {

}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "an orc knuckle"
Creature.special_loot = {

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10643,
    10644,
    10650,
    10651,
    10652,
    10653,
    10654,
    10655,
    10656,
    10657,
    10647,
    10648,
    10649,
    10658,
    10659,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10643,
    10644,
    10650,
    10651,
    10652,
    10653,
    10654,
    10655,
    10656,
    10657,
    10647,
    10648,
    10649,
    10658,
    10659,
}

Creature.roam_chance     = 20   -- % chance to move each tick
Creature.respawn_seconds = 300
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Taller than a common human and of substantially heavier build, the Neartofar orc has a build of solid bone and gristle.  Piercing yellow eyes glare angrily under a thick bony ridge.  His arms resemble thick twisted tree trunks ending in ragged gore-crusted claws."

return Creature
