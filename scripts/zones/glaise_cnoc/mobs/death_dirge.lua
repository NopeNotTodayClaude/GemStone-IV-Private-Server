-- Creature: death dirge
-- Zone: glaise_cnoc  |  Level: 9
local Creature = {}

Creature.id              = 2002
Creature.name            = "death dirge"
Creature.level           = 9
Creature.family          = "humanoid"
Creature.classification  = "corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 95
Creature.hp_variance     = 8

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 14
Creature.ds_bolt         = 17
Creature.td_spiritual    = 27
Creature.td_elemental    = 27
Creature.udf             = 66
Creature.armor_asg       = 8
Creature.armor_natural   = true

Creature.attacks = {
    { type = "closed_fist", as = 98, damage_type = "crush" },
}

Creature.spells = {
    { name = "Calm (201)", cs = 53, as = 0 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {

}

Creature.immune = {
    "disease",
    "poison",
}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a dirge skin"
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

Creature.roam_chance     = 20   -- % chance to move each tick
Creature.respawn_seconds = 300
Creature.max_count       = 6

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Defender of a battleground long lost in the terrain, the death dirge still maintains its post relentlessly, battling all that would attempt to invade its position.  Only the orders to repel all who enter remain in its consciousness."

return Creature
