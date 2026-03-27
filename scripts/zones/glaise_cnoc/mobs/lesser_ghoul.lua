-- Creature: lesser ghoul
-- Zone: glaise_cnoc  |  Level: 1
local Creature = {}

Creature.id              = 1001
Creature.name            = "lesser ghoul"
Creature.level           = 1
Creature.family          = "ghoul"
Creature.classification  = "corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 40
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 0
Creature.ds_bolt         = -3
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 44
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 31, damage_type = "slash" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "ghoul_rot_chance",
}

Creature.immune = {
    "disease",
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
    "ghoul nail",
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

Creature.roam_chance     = 25   -- % chance to move each tick
Creature.respawn_seconds = 240
Creature.max_count       = 8

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Resembling a decaying corpse, the lesser ghoul is hunched over so that its long arms trail along the ground.  Sharp claw-like nails tip both hands and feet and the stench of corruption wafts thickly from the sodden rags of clothing that cling to its leprous body."

return Creature
