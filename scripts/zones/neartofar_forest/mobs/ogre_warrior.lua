-- Creature: ogre warrior
-- Zone: neartofar_forest  |  Level: 20
local Creature = {}

Creature.id              = 6004
Creature.name            = "ogre warrior"
Creature.level           = 20
Creature.family          = "ogre"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 250
Creature.hp_variance     = 20

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 131
Creature.ds_bolt         = 90
Creature.td_spiritual    = 60
Creature.td_elemental    = 60
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false

Creature.attacks = {
    { type = "mace", as = 201, damage_type = "crush" },
    { type = "military_pick", as = 193, damage_type = "puncture" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "sunder_shield",
    "essence_shard_drop",
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
Creature.skin            = "an ogre tooth"
Creature.special_loot = {
    "glimmering blue essence shard",
}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10660,
    10661,
    10662,
    10663,
    10664,
    10665,
    10666,
    10667,
    10643,
    10644,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10660,
    10661,
    10662,
    10663,
    10664,
    10665,
    10666,
    10667,
    10643,
    10644,
    10656,
    10657,
}

Creature.roam_chance     = 10   -- % chance to move each tick
Creature.respawn_seconds = 420
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The ogre warrior's bulging muscles and long arms give it an advantage in any encounter.  The heavy, rock-hard skin serves equally well as armor or to keep itself dry from the elements.  Dark, smoking eyes glare out as it challenges any to oppose it."

return Creature
