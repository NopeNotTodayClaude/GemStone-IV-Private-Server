-- Creature: frost giant
-- Zone: Icemule Trace / Glatoph Deep  |  Level: 38
local Creature = {}
Creature.id              = 10314
Creature.name            = "frost giant"
Creature.level           = 38
Creature.family          = "giant"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 480
Creature.hp_variance     = 40
Creature.ds_melee        = 305
Creature.ds_bolt         = 150
Creature.td_spiritual    = 120
Creature.td_elemental    = 120
Creature.udf             = 0
Creature.armor_asg       = 13
Creature.armor_natural   = false
Creature.attacks         = {
    { type="ice_spear", as=468, damage_type="puncture" },
    { type="fist", as=460, damage_type="crush" },
    { type="blizzard_blast", as=450, damage_type="cold" },
}
Creature.spells          = {
    { name="blizzard", cs=192, as=0 },
    { name="ice_bolt", cs=185, as=0 },
}
Creature.abilities       = {
    "blizzard_call",
    "cold_immunity",
    "ice_stomp",
    "hurl_glacier",
}
Creature.immune          = {
    "cold",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a frost giant ice shard"
Creature.special_loot    = {
    "a frost giant runic ice tablet",
    "a glacier-forged weapon fragment",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    7869,
    7870,
    7871,
    7872,
    7902,
    7903,
    7904,
    7905,
    30516,
    30517,
    30518,
    30519
    }
Creature.roam_rooms      = {
    7869,
    7870,
    7871,
    7872,
    7902,
    7903,
    7904,
    7905,
    30516,
    30517,
    30518,
    30519
    }
Creature.roam_chance     = 8
Creature.respawn_seconds = 720
Creature.max_count       = 1
Creature.description     = "The frost giant stands thirty feet of pale blue-grey muscle, armoured in plates of magically-hardened ice that reform within minutes of being shattered.  The spear it carries is an icicle the size of a log, and the blizzard it can summon with a gesture is localised but functionally lethal.  It speaks in a language that sounds like the cracking of glacial ice, and its breath is a visible plume even in the depths of Glatoph."
return Creature
