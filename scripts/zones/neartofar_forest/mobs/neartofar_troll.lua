-- Creature: Neartofar troll
-- Zone: neartofar_forest  |  Level: 15
local Creature = {}

Creature.id              = 6003
Creature.name            = "Neartofar troll"
Creature.level           = 15
Creature.family          = "troll"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 200
Creature.hp_variance     = 15

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 127
Creature.ds_bolt         = 0
Creature.td_spiritual    = 52
Creature.td_elemental    = 52
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false

Creature.attacks = {
    { type = "longsword", as = 179, damage_type = "slash" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "spirit_warding_2",
    "troll_regeneration",
}

Creature.immune = {

}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a greasy troll scalp"
Creature.special_loot = {

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10643,
    10644,
    10650,
    10651,
    10652,
    10653,
    10643,
    10644,
    10656,
    10657,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10643,
    10644,
    10650,
    10651,
    10652,
    10653,
    10654,
    10655,
    10656,
    10657,
    10643,
    10644,
    10656,
    10657,
}

Creature.roam_chance     = 15   -- % chance to move each tick
Creature.respawn_seconds = 360
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Huge and dangerous, the Neartofar troll towers above even a tall giantman.  Brown and green pigmented skin so thick it serves well as armor covers most of it.  No light of intellect glows in its narrow piggish eyes — only the lust for slaughter."

return Creature
