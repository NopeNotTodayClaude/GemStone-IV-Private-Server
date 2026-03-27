-- Creature: firephantom
-- Zone: Vornavis / North Beach  |  Level: 6
local Creature = {}
Creature.id              = 10107
Creature.name            = "firephantom"
Creature.level           = 6
Creature.family          = "phantom"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 90
Creature.hp_variance     = 7
Creature.ds_melee        = 70
Creature.ds_bolt         = 35
Creature.td_spiritual    = 20
Creature.td_elemental    = 12
Creature.udf             = 68
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="fire_touch", as=88, damage_type="fire" },
    { type="spectral_touch", as=82, damage_type="unbalancing" },
}
Creature.spells          = {}
Creature.abilities       = {
    "spirit_strike",
    "fire_touch",
    "flame_burst",
    "phase_through_terrain",
}
Creature.immune          = {
    "disease",
    "poison",
    "fire",
}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = ""
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = true
Creature.decay_message   = "flares brightly and gutters out."
Creature.spawn_rooms     = {
    7613,
    7615,
    7616,
    7619,
    7632,
    7633,
    7634,
    7637,
    7638,
    7639,
    7640,
    7641,
    7642,
    7643,
    7644,
    7654,
    7707,
    7712,
    7713,
    7714
    }
Creature.roam_rooms      = {
    7613,
    7615,
    7616,
    7619,
    7632,
    7633,
    7634,
    7637,
    7638,
    7639,
    7640,
    7641,
    7642,
    7643,
    7644,
    7654,
    7707,
    7712,
    7713,
    7714
    }
Creature.roam_chance     = 22
Creature.respawn_seconds = 240
Creature.max_count       = 4
Creature.description     = "A living flame given spectral form, the firephantom drifts above the beach and lagoon with the erratic movement of an actual fire in wind.  The core burns white-hot while the edges feather into orange and yellow, and the outline of a humanoid form is only intermittently visible within the conflagration.  The heat it radiates is real and uncomfortable at twenty feet."
return Creature
