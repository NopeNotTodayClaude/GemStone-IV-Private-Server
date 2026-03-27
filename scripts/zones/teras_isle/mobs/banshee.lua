-- Creature: banshee
-- Zone: Teras Isle / Mausoleum Catacombs  |  Level: 50
local Creature = {}
Creature.id              = 10204
Creature.name            = "banshee"
Creature.level           = 50
Creature.family          = "banshee"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 600
Creature.hp_variance     = 50
Creature.ds_melee        = 380
Creature.ds_bolt         = 192
Creature.td_spiritual    = 162
Creature.td_elemental    = 108
Creature.udf             = 385
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="wail", as=475, damage_type="unbalancing" },
    { type="spectral_touch", as=468, damage_type="cold" },
    { type="death_scream", as=460, damage_type="unbalancing" },
}
Creature.spells          = {
    { name="banshee_wail", cs=252, as=0 },
    { name="terror", cs=248, as=0 },
    { name="death_keen", cs=244, as=0 },
}
Creature.abilities       = {
    "spirit_strike",
    "banshee_wail",
    "death_scream",
    "phase_through_terrain",
    "fear_aura",
    "soul_rend",
}
Creature.immune          = {
    "disease",
    "poison",
    "cold",
    "electricity",
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
Creature.decay_message   = "releases one final, ear-splitting shriek before dissolving into nothing."
Creature.spawn_rooms     = {
    2283,
    2284,
    2285,
    2286,
    2287,
    2288,
    2289,
    2290,
    2291,
    2292,
    2293,
    2294,
    2295,
    2296,
    2297,
    2298,
    2299
    }
Creature.roam_rooms      = {
    2283,
    2284,
    2285,
    2286,
    2287,
    2288,
    2289,
    2290,
    2291,
    2292,
    2293,
    2294,
    2295,
    2296,
    2297,
    2298,
    2299
    }
Creature.roam_chance     = 10
Creature.respawn_seconds = 900
Creature.max_count       = 2
Creature.description     = "The banshee's cry can be heard before the creature is seen — a wail that starts at the edge of human hearing and rises to a pitch that seems to resonate directly in the bones and the teeth.  Its form is that of a woman in white robes that are always in motion, as though blown by a wind that affects only her.  The face, when it turns toward you, is a mask of absolute grief that somehow reads as a threat."
return Creature
