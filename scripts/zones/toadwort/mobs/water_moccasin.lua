-- Creature: water moccasin
-- Zone: toadwort  |  Level: 4
local Creature = {}

Creature.id              = 7004
Creature.name            = "water moccasin"
Creature.level           = 4
Creature.family          = "reptilian"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "ophidian"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 50
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 37
Creature.ds_bolt         = 0
Creature.td_spiritual    = 12
Creature.td_elemental    = 12
Creature.udf             = 0
Creature.armor_asg       = 5
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 68, damage_type = "puncture" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "venom",
    "swim",
}

Creature.immune = {
    "poison",
}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a water moccasin skin"
Creature.special_loot = {

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10523,
    10524,
    10525,
    10526,
    10527,
    10528,
    10529,
    10530,
    10531,
    10532,
    10533,
    10534,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10522,
    10523,
    10524,
    10525,
    10526,
    10527,
    10528,
    10529,
    10530,
    10531,
    10532,
    10533,
    10534,
    10535,
    10536,
}

Creature.roam_chance     = 25   -- % chance to move each tick
Creature.respawn_seconds = 240
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The water moccasin appears to be at least three feet long, with dark olive-colored skin and a faint diamond pattern.  When the mouth opens you can see a sickly white lining within."

return Creature
