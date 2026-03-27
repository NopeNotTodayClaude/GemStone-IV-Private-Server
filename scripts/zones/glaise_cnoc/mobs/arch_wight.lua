-- Creature: arch wight
-- Zone: glaise_cnoc  |  Level: 20
local Creature = {}

Creature.id              = 2008
Creature.name            = "arch wight"
Creature.level           = 20
Creature.family          = "wight"
Creature.classification  = "corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 170
Creature.hp_variance     = 12

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 113
Creature.ds_bolt         = 55
Creature.td_spiritual    = 63
Creature.td_elemental    = 63
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false

Creature.attacks = {
    { type = "scimitar", as = 156, damage_type = "slash" },
    { type = "claw", as = 136, damage_type = "slash" },
}

Creature.spells = {
    { name = "Mind Jolt (706)", cs = 123, as = 0 },
    { name = "Empathy (1108)", cs = 120, as = 0 },
    { name = "Earthen Fury (917)", cs = 0, as = 140 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "spirit_warding_2",
    "spell_shield_219",
    "earthen_fury_caster",
    "gas_cloud",
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
Creature.skin            = "a wight skin"
Creature.special_loot = {

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10737,
    10738,
    10739,
    10740,
    10741,
    10742,
    10743,
    10744,
    10745,
    10746,
    10747,
    10748,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10737,
    10738,
    10739,
    10740,
    10741,
    10742,
    10743,
    10744,
    10745,
    10746,
    10747,
    10748,
}

Creature.roam_chance     = 10   -- % chance to move each tick
Creature.respawn_seconds = 480
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The arch wight moves ponderously, its gaunt humanoid frame often bent nearly double.  Massive upper arms contrast with a thin torso.  Liquid golden eyes filled with tiny red sparks and the lack of flesh on its face gives it a horrific toothy grin."

return Creature
