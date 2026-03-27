-- Creature: bobcat
-- Zone: toadwort  |  Level: 5
local Creature = {}

Creature.id              = 7005
Creature.name            = "bobcat"
Creature.level           = 5
Creature.family          = "feline"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "quadruped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 60
Creature.hp_variance     = 6

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 44
Creature.ds_bolt         = 0
Creature.td_spiritual    = 15
Creature.td_elemental    = 15
Creature.udf             = 71
Creature.armor_asg       = 6
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 80, damage_type = "puncture" },
    { type = "claw", as = 90, damage_type = "slash" },
    { type = "charge", as = 90, damage_type = "crush" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "pounce",
}

Creature.immune = {

}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a bobcat claw"
Creature.special_loot = {

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10499,
    10500,
    10501,
    10502,
    10503,
    10504,
    10531,
    10532,
    10533,
    10534,
    10535,
    10536,
    10537,
    10538,
    10539,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10499,
    10500,
    10501,
    10502,
    10503,
    10504,
    10531,
    10532,
    10533,
    10534,
    10535,
    10536,
    10537,
    10538,
    10539,
}

Creature.roam_chance     = 35   -- % chance to move each tick
Creature.respawn_seconds = 300
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Twice the size of a domestic cat, the bobcat is covered in dense, thick fur varying from soft greys to light reddish brown.  Deep brown spots mark the bobcat's pelt.  Whisking back and forth with her short banded tail, the bobcat seems anxious to pounce."

return Creature
