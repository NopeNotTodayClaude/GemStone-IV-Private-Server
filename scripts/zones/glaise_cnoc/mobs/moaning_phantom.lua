-- Creature: moaning phantom
-- Zone: glaise_cnoc  |  Level: 2
local Creature = {}

Creature.id              = 1003
Creature.name            = "moaning phantom"
Creature.level           = 2
Creature.family          = "ghost"
Creature.classification  = "non_corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 44
Creature.hp_variance     = 4

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = -26
Creature.ds_bolt         = -28
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "closed_fist", as = 28, damage_type = "crush" },
}

Creature.spells = {
    { name = "Minor Shock (901)", cs = 0, as = 50 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "non_corporeal",
    "phase",
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

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    5834,
    5835,
    5836,
    5837,
    5838,
    5839,
    5840,
    5841,
    5842,
    5843,
    5844,
    5845,
    5846,
    5847,
    5848,
    5849,
    5850,
    5851,
    5852,
    5853,
    5854,
    5855,
    5856,
    5857,
    5858,
    5859,
    5860,
    5861,
    5862,
    5863,
    5864,
    5865,
    5866,
    5867,
    5891,
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
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    5834,
    5835,
    5836,
    5837,
    5838,
    5839,
    5840,
    5841,
    5842,
    5843,
    5844,
    5845,
    5846,
    5847,
    5848,
    5849,
    5850,
    5851,
    5852,
    5853,
    5854,
    5855,
    5856,
    5857,
    5858,
    5859,
    5860,
    5861,
    5862,
    5863,
    5864,
    5865,
    5866,
    5867,
    5891,
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
}

Creature.roam_chance     = 30   -- % chance to move each tick
Creature.respawn_seconds = 270
Creature.max_count       = 5

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Barely still connected to the living plane, the moaning phantom flickers in and out as it confronts intruders.  The outlines of its shape are barely apparent, but what is visible suggests a once-humanoid appearance caught in a continuous scream of anguish."

return Creature
