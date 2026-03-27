-- Creature: troll wraith
-- Zone: Zul Logoth / Troll Burial Grounds  |  Level: 35
local Creature = {}
Creature.id              = 10404
Creature.name            = "troll wraith"
Creature.level           = 35
Creature.family          = "wraith"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 448
Creature.hp_variance     = 37
Creature.ds_melee        = 288
Creature.ds_bolt         = 142
Creature.td_spiritual    = 118
Creature.td_elemental    = 82
Creature.udf             = 298
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="wraith_touch", as=348, damage_type="unbalancing" },
    { type="regeneration_drain", as=340, damage_type="cold" },
}
Creature.spells          = {
    { name="wither", cs=178, as=0 },
    { name="wraith_wail", cs=172, as=0 },
}
Creature.abilities       = {
    "spirit_strike",
    "regeneration_drain",
    "phase_through_terrain",
    "fear_aura",
}
Creature.immune          = {
    "disease",
    "poison",
    "cold",
}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = ""
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = true
Creature.decay_message   = "tears apart with a sound like tearing stone."
Creature.spawn_rooms     = {
    5811,
    5812,
    5813,
    5814,
    5815,
    5816,
    5817,
    5818,
    5819,
    5820,
    5821,
    5822
    }
Creature.roam_rooms      = {
    5811,
    5812,
    5813,
    5814,
    5815,
    5816,
    5817,
    5818,
    5819,
    5820,
    5821,
    5822,
    5752,
    5753,
    5754
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 600
Creature.max_count       = 1
Creature.description     = "A troll's wraith is an unsettling thing — the tremendous life force that normally sustains troll regeneration has been twisted into its opposite, a drain rather than a restoration.  The form retains the size and proportions of the living troll, but rendered in shadow and given a hunger for the vitality it no longer possesses.  What remains of the regenerative ability now inverts: it heals itself from the health it steals from others."
return Creature
