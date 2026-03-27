-- Creature: gaunt spectral servant
-- Zone: Marsh Keep  |  Level: 44
local Creature = {}
Creature.id              = 10014
Creature.name            = "gaunt spectral servant"
Creature.level           = 44
Creature.family          = "spectre"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 540
Creature.hp_variance     = 45
Creature.ds_melee        = 348
Creature.ds_bolt         = 178
Creature.td_spiritual    = 148
Creature.td_elemental    = 100
Creature.udf             = 360
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="spectral_touch", as=428, damage_type="unbalancing" },
    { type="chill_strike", as=420, damage_type="cold" },
}
Creature.spells          = {
    { name="spirit_slayer", cs=222, as=0 },
    { name="wither", cs=215, as=0 },
}
Creature.abilities       = {
    "spirit_strike",
    "phase_through_terrain",
    "fear_aura",
    "life_leech",
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
Creature.loot_boxes      = false
Creature.skin            = ""
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = true
Creature.decay_message   = "fades with a faint moan."
Creature.spawn_rooms     = {
    11683,
    11684,
    11685,
    11686,
    11687,
    11688,
    11689,
    11691,
    11692,
    11693,
    11694,
    11696,
    16214,
    11695,
    11697,
    11698,
    11699,
    11700,
    11701,
    11702,
    11703,
    11704,
    11705,
    11706,
    11707,
    11708,
    11709,
    11710
    }
Creature.roam_rooms      = {
    11683,
    11684,
    11685,
    11686,
    11687,
    11688,
    11689,
    11691,
    11692,
    11693,
    11694,
    11696,
    16214,
    11695,
    11697,
    11698,
    11699,
    11700,
    11701,
    11702,
    11703,
    11704,
    11705,
    11706,
    11707,
    11708,
    11709,
    11710
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 600
Creature.max_count       = 6
Creature.description     = "The gaunt spectral servant was, in life, one of the many who served the keep.  In unlife it still performs the motions of service — moving through the halls, pausing at doors, ascending stairs — while the consciousness that drives it has been replaced by something that hates the living with cold, implacable intensity.  The spectral form is wasted and stretched, the features barely recognizable as humanoid."
return Creature
