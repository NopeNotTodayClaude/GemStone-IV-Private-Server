-- Creature: Mistydeep siren
-- Zone: toadwort  |  Level: 2
local Creature = {}

Creature.id              = 7002
Creature.name            = "Mistydeep siren"
Creature.level           = 2
Creature.family          = "fey"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 42
Creature.hp_variance     = 4

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 20
Creature.ds_bolt         = 18
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = false

Creature.attacks = {
    { type = "dagger", as = 50, damage_type = "puncture" },
}

Creature.spells = {
    { name = "Calm (201)", cs = 10, as = 0 },
    { name = "Vibration Chant (1002)", cs = 2, as = 0 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "glamour",
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
Creature.skin            = ""
Creature.special_loot = {
    "pristine nymph's hair",
}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
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
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
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

Creature.roam_chance     = 20   -- % chance to move each tick
Creature.respawn_seconds = 270
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The Mistydeep siren's pale eyes melt to a warm blue as she transfixes her gaze on victims.  She uses her melodious voice to allure.  From a distance she appears a beautiful maiden, but without glamour her bluish corpselike skin reveals her true nature."

return Creature
