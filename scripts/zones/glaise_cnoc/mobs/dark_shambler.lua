-- Creature: dark shambler
-- Zone: glaise_cnoc  |  Level: 17
local Creature = {}

Creature.id              = 2007
Creature.name            = "dark shambler"
Creature.level           = 17
Creature.family          = "humanoid"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 200
Creature.hp_variance     = 15

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 108
Creature.ds_bolt         = 94
Creature.td_spiritual    = 51
Creature.td_elemental    = 51
Creature.udf             = 121
Creature.armor_asg       = 12
Creature.armor_natural   = false

Creature.attacks = {
    { type = "two_handed_sword", as = 175, damage_type = "slash" },
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
Creature.skin            = "a glistening black eye"
Creature.special_loot = {

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
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
    10729,
    10730,
    10731,
    10732,
    10733,
    10734,
    10735,
    10736,
    10737,
    10738,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
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
    10729,
    10730,
    10731,
    10732,
    10733,
    10734,
    10735,
    10736,
    10737,
    10738,
}

Creature.roam_chance     = 15   -- % chance to move each tick
Creature.respawn_seconds = 360
Creature.max_count       = 4

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Very little of the dark shambler is not thickly muscled.  This squat humanoid lumbers through the countryside, surveying the world through glistening black eyes.  Its entirely black skin appears to absorb light rather than reflect it."

return Creature
