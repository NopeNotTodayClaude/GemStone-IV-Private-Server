-- Creature: greater ghoul
-- Zone: glaise_cnoc  |  Level: 3
local Creature = {}

Creature.id              = 1005
Creature.name            = "greater ghoul"
Creature.level           = 3
Creature.family          = "ghoul"
Creature.classification  = "corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 60
Creature.hp_variance     = 6

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 12
Creature.ds_bolt         = 8
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 50
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 63, damage_type = "slash" },
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
Creature.skin            = "a ghoul scraping"
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

Creature.roam_chance     = 25   -- % chance to move each tick
Creature.respawn_seconds = 270
Creature.max_count       = 6

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Larger and meaner than its lesser brethren, the greater ghoul shambles along with filth-encrusted claws and ragged bits of decaying flesh hanging from sharp fangs.  A few filthy bits of rotting cloth still cling to its diseased and festering body."

return Creature
