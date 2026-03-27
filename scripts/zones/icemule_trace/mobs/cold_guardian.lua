-- Creature: cold guardian
-- Zone: Icemule Trace / Cave of Ice  |  Level: 34
local Creature = {}
Creature.id              = 10316
Creature.name            = "cold guardian"
Creature.level           = 34
Creature.family          = "elemental"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 432
Creature.hp_variance     = 36
Creature.ds_melee        = 272
Creature.ds_bolt         = 132
Creature.td_spiritual    = 110
Creature.td_elemental    = 110
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = true
Creature.attacks         = {
    { type="ice_fist", as=420, damage_type="cold" },
    { type="ice_blade", as=412, damage_type="slash" },
    { type="freeze_touch", as=404, damage_type="cold" },
}
Creature.spells          = {
    { name="ice_bolt", cs=168, as=0 },
    { name="flash_freeze", cs=162, as=0 },
}
Creature.abilities       = {
    "cold_immunity",
    "freeze_touch",
    "ice_blade",
    "cold_aura",
}
Creature.immune          = {
    "cold",
}
Creature.resist          = {
    "fire",
}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a guardian ice shard"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = true
Creature.decay_message   = "shatters into fragments of ice that immediately melt."
Creature.spawn_rooms     = {
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
    7868
    }
Creature.roam_rooms      = {
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
    7868
    }
Creature.roam_chance     = 10
Creature.respawn_seconds = 600
Creature.max_count       = 2
Creature.description     = "A guardian elemental formed from the deep ice of Glatoph, the cold guardian appears as a roughly humanoid form of absolute transparency — the internal structure of crystalline ice visible in its depths.  The weapons it wields are formed from its own substance and reform almost immediately after shattering.  Its presence alone lowers ambient temperature to dangerous levels."
return Creature
