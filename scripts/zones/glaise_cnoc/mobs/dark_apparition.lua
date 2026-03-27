-- Creature: dark apparition
-- Zone: glaise_cnoc  |  Level: 5
local Creature = {}

Creature.id              = 1008
Creature.name            = "dark apparition"
Creature.level           = 5
Creature.family          = "ghost"
Creature.classification  = "non_corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 65
Creature.hp_variance     = 6

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 51
Creature.ds_bolt         = -20
Creature.td_spiritual    = 15
Creature.td_elemental    = 15
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 48, damage_type = "puncture" },
    { type = "claw", as = 58, damage_type = "slash" },
}

Creature.spells = {
    { name = "Blood Burst (701)", cs = 46, as = 0 },
    { name = "Mana Disruption (702)", cs = 46, as = 0 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "non_corporeal",
    "rapid_decay",
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
Creature.decay_seconds   = 10
Creature.crumbles        = true   -- body vanishes on death
Creature.decay_message   = "The dark apparition's form rapidly dissolves into shadow and is gone."

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10685,
    10686,
    10687,
    10688,
    10689,
    10690,
    10691,
    10692,
    10693,
    10685,
    5879,
    5887,
    5886,
    5885,
    5884,
    5889,
    5883,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10685,
    10686,
    10687,
    10688,
    10689,
    10690,
    10691,
    10692,
    10693,
    5879,
    5887,
    5886,
    5885,
}

Creature.roam_chance     = 10   -- % chance to move each tick
Creature.respawn_seconds = 360
Creature.max_count       = 3

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "It is difficult to focus on the dark apparition.  It wavers and shifts as an image seen through dark waters — each form it assumes has some aspect of horror and bloody death.  One form is that of a corpse mutilated beyond words, another a waif horribly burned and scarred."

return Creature
