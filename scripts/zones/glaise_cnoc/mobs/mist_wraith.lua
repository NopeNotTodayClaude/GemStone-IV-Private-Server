-- Creature: mist wraith
-- Zone: glaise_cnoc  |  Level: 5
local Creature = {}

Creature.id              = 1007
Creature.name            = "mist wraith"
Creature.level           = 5
Creature.family          = "wraith"
Creature.classification  = "non_corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 80
Creature.hp_variance     = 8

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 10
Creature.ds_bolt         = -8
Creature.td_spiritual    = 15
Creature.td_elemental    = 15
Creature.udf             = 2
Creature.armor_asg       = 8
Creature.armor_natural   = true

Creature.attacks = {
    { type = "closed_fist", as = 81, damage_type = "crush" },
    { type = "claw", as = 71, damage_type = "slash" },
    { type = "ensnare", as = 71, damage_type = "crush" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "non_corporeal",
    "spirit_drain",
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
Creature.skin            = "mist wraith eye"
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
    5888,
    5860,
    5882,
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
    5888,
    5860,
    5882,
}

Creature.roam_chance     = 20   -- % chance to move each tick
Creature.respawn_seconds = 300
Creature.max_count       = 4

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The smaller cousin to the normal wraith, the mist wraith is the spirit of a soldier vanquished in great battle.  The spirits trap the local mist to give them a semi-physical form with which to exact vengeance."

return Creature
