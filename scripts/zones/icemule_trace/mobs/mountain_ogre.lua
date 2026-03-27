-- Creature: mountain ogre
-- Zone: Icemule Trace / Glatoph  |  Level: 16
local Creature = {}
Creature.id              = 10312
Creature.name            = "mountain ogre"
Creature.level           = 16
Creature.family          = "ogre"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 202
Creature.hp_variance     = 16
Creature.ds_melee        = 140
Creature.ds_bolt         = 66
Creature.td_spiritual    = 51
Creature.td_elemental    = 51
Creature.udf             = 0
Creature.armor_asg       = 9
Creature.armor_natural   = false
Creature.attacks         = {
    { type="greatclub", as=196, damage_type="crush" },
    { type="fist", as=188, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "powerful_blow",
    "sunder_shield",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "an ogre tusk"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    7843,
    7844,
    7845,
    7846,
    7847,
    7848,
    7849,
    7850,
    7851,
    7853,
    7854,
    7855,
    7856,
    7857,
    7858,
    7859,
    7860,
    7861,
    7867,
    7868,
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
    7843,
    7844,
    7845,
    7846,
    7847,
    7848,
    7849,
    7850,
    7851,
    7853,
    7854,
    7855,
    7856,
    7857,
    7858,
    7859,
    7860,
    7861,
    7867,
    7868,
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
Creature.roam_chance     = 15
Creature.respawn_seconds = 360
Creature.max_count       = 4
Creature.description     = "The mountain ogres of Glatoph are barrel-chested and thick-limbed, built for altitude and cold rather than the temperate grasslands their lowland cousins inhabit.  The fur that covers them is their own, grown thick over generations, and the greatclubs they carry are fashioned from the dense wood of the few trees that survive the altitude.  They are not strategists, but they are persistent."
return Creature
