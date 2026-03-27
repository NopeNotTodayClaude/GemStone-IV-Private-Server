-- Creature: arctic titan
-- Zone: Icemule Trace / Glatoph Deep  |  Level: 36
local Creature = {}
Creature.id              = 10313
Creature.name            = "arctic titan"
Creature.level           = 36
Creature.family          = "giant"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 455
Creature.hp_variance     = 37
Creature.ds_melee        = 290
Creature.ds_bolt         = 142
Creature.td_spiritual    = 115
Creature.td_elemental    = 115
Creature.udf             = 0
Creature.armor_asg       = 13
Creature.armor_natural   = false
Creature.attacks         = {
    { type="greatclub", as=445, damage_type="crush" },
    { type="stomp", as=438, damage_type="crush" },
    { type="ice_throw", as=428, damage_type="cold" },
}
Creature.spells          = {}
Creature.abilities       = {
    "giant_stomp",
    "ice_throw",
    "cold_immunity",
    "powerful_blow",
}
Creature.immune          = {
    "cold",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "an arctic titan frost shard"
Creature.special_loot    = {
    "a glacier-polished runestone",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
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
Creature.roam_chance     = 8
Creature.respawn_seconds = 660
Creature.max_count       = 2
Creature.description     = "The arctic titan is the apex of the cold-adapted giant lineage — a twenty-five foot creature that has been shaped by the deep glacier into something as much geological as biological.  The skin is grey-white stone-hard, the hair is frost-rime and wind-tangled, and the eyes hold the pale blue of deep ice.  It moves through deep-freeze temperatures with no visible discomfort because, for it, this is simply comfortable."
return Creature
