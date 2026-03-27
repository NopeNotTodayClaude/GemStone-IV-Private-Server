-- Creature: fire guardian
-- Zone: Vornavis / North Beach  |  Level: 16
local Creature = {}
Creature.id              = 10108
Creature.name            = "fire guardian"
Creature.level           = 16
Creature.family          = "elemental"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 202
Creature.hp_variance     = 16
Creature.ds_melee        = 142
Creature.ds_bolt         = 68
Creature.td_spiritual    = 51
Creature.td_elemental    = 51
Creature.udf             = 8
Creature.armor_asg       = 3
Creature.armor_natural   = true
Creature.attacks         = {
    { type="fire_strike", as=195, damage_type="fire" },
    { type="claw", as=188, damage_type="slash" },
}
Creature.spells          = {
    { name="fire_bolt", cs=88, as=0 },
    { name="immolate", cs=82, as=0 },
}
Creature.abilities       = {
    "flame_aura",
    "fire_bolt",
    "heat_wave",
}
Creature.immune          = {
    "fire",
}
Creature.resist          = {
    "cold",
}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = ""
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = true
Creature.decay_message   = "collapses in a shower of embers."
Creature.spawn_rooms     = {
    7603,
    7604,
    7605,
    7606,
    7607,
    7608,
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
    7713
    }
Creature.roam_rooms      = {
    7603,
    7604,
    7605,
    7606,
    7607,
    7608,
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
    7713
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 360
Creature.max_count       = 3
Creature.description     = "A figure of condensed fire shaped roughly like a warrior in armour, the fire guardian stands taller than a human and radiates heat visible as a shimmer in the air for thirty feet in every direction.  The 'armour' it appears to wear is in fact denser concentrations of its own substance, and the weapons it carries are likewise formed from itself.  Fire of its own element feeds rather than harms it."
return Creature
