-- Creature: dark vysan
-- Zone: glaise_cnoc  |  Level: 3
local Creature = {}

Creature.id              = 1004
Creature.name            = "dark vysan"
Creature.level           = 3
Creature.family          = "vysan"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 60
Creature.hp_variance     = 6

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 22
Creature.ds_bolt         = 17
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "ensnare", as = 54, damage_type = "crush" },
    { type = "pound", as = 44, damage_type = "crush" },
    { type = "charge", as = 54, damage_type = "crush" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "cold_flare",
    "fire_immune",
    "float",
}

Creature.immune = {
    "fire",
    "disease",
    "poison",
}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = false
Creature.loot_boxes      = true
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
    5868,
    5869,
    5870,
    5871,
    5872,
    5873,
    5874,
    5875,
    5876,
    5877,
    5878,
    5879,
    5880,
    5881,
    5882,
    5883,
    5884,
    5885,
    5886,
    5887,
    5888,
    5889,
    5890,
    5891,
    5892,
    5893,
    24559,
    29574,
    29575,
    29576,
    5867,
    5879,
    5882,
    5890,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    5868,
    5869,
    5870,
    5871,
    5872,
    5873,
    5874,
    5875,
    5876,
    5877,
    5878,
    5879,
    5880,
    5881,
    5882,
    5883,
    5884,
    5885,
    5886,
    5887,
    5888,
    5889,
    5890,
    5891,
    5892,
    5893,
    24559,
    29574,
    29575,
    29576,
    5867,
    5879,
    5882,
    5890,
}

Creature.roam_chance     = 15   -- % chance to move each tick
Creature.respawn_seconds = 300
Creature.max_count       = 4

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The dark vysan is peculiar and dapple grey, extremely bloated with gas so it floats from place to place.  Its appendages extend straight out from its rotund body and its head resembles an overturned kettle.  Afraid of bright light, it prefers darker areas."

return Creature
