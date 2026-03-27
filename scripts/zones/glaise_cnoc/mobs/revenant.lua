-- Creature: revenant
-- Zone: glaise_cnoc  |  Level: 4
local Creature = {}

Creature.id              = 1006
Creature.name            = "revenant"
Creature.level           = 4
Creature.family          = "ghost"
Creature.classification  = "non_corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 57
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = -29
Creature.ds_bolt         = -35
Creature.td_spiritual    = 12
Creature.td_elemental    = 12
Creature.udf             = 22
Creature.armor_asg       = 7
Creature.armor_natural   = true

Creature.attacks = {
    { type = "closed_fist", as = 57, damage_type = "crush" },
    { type = "broadsword", as = 0, damage_type = "slash" },
}

Creature.spells = {
    { name = "Blood Burst (701)", cs = 40, as = 0 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "non_corporeal",
    "cold_immune",
}

Creature.immune = {
    "disease",
    "poison",
    "cold",
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

Creature.roam_chance     = 20   -- % chance to move each tick
Creature.respawn_seconds = 300
Creature.max_count       = 4

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The revenant howls in pain, remembering its grisly demise.  It presents a ghostly visage of skin shredded by the torturer's whip to display exposed muscles, shriveled organs, and protruding bones."

return Creature
