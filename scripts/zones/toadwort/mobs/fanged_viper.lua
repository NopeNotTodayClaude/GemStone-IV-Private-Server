-- Creature: fanged viper
-- Zone: toadwort  |  Level: 4
local Creature = {}

Creature.id              = 7003
Creature.name            = "fanged viper"
Creature.level           = 4
Creature.family          = "reptilian"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "ophidian"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 50
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 37
Creature.ds_bolt         = 33
Creature.td_spiritual    = 12
Creature.td_elemental    = 12
Creature.udf             = 51
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
Creature.skin            = "a viper skin"
Creature.special_loot = {

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10505,
    10506,
    10507,
    10508,
    10509,
    10510,
    10511,
    10512,
    10513,
    10514,
    10515,
    10516,
    10517,
    10518,
    10519,
    10520,
    10521,
    10522,
    10523,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10505,
    10506,
    10507,
    10508,
    10509,
    10510,
    10511,
    10512,
    10513,
    10514,
    10515,
    10516,
    10517,
    10518,
    10519,
    10520,
    10521,
    10522,
    10523,
    10524,
    10525,
}

Creature.roam_chance     = 25   -- % chance to move each tick
Creature.respawn_seconds = 240
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The fanged viper slithers quickly through the landscape, its massive venomous fangs hidden by small flaps of skin.  Once its ire is aroused, the flaps pull back revealing the true monster.  Death rapidly awaits any who doubt its abilities."

return Creature
