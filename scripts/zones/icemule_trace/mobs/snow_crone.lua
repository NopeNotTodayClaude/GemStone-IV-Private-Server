-- Creature: snow crone
-- Zone: Icemule Trace / Glatoph Deep  |  Level: 36
local Creature = {}
Creature.id              = 10315
Creature.name            = "snow crone"
Creature.level           = 36
Creature.family          = "humanoid"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 452
Creature.hp_variance     = 37
Creature.ds_melee        = 285
Creature.ds_bolt         = 140
Creature.td_spiritual    = 114
Creature.td_elemental    = 114
Creature.udf             = 0
Creature.armor_asg       = 6
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=440, damage_type="slash" },
    { type="ice_touch", as=432, damage_type="cold" },
}
Creature.spells          = {
    { name="blizzard", cs=180, as=0 },
    { name="ice_bolt", cs=175, as=0 },
    { name="flash_freeze", cs=170, as=0 },
    { name="curse", cs=165, as=0 },
}
Creature.abilities       = {
    "cold_immunity",
    "flash_freeze",
    "hag_curse",
    "blizzard_call",
}
Creature.immune          = {
    "cold",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a snow crone fingernail"
Creature.special_loot    = {
    "a carved bone focus",
    "a vial of glacial meltwater",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
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
Creature.roam_chance     = 10
Creature.respawn_seconds = 660
Creature.max_count       = 3
Creature.description     = "The snow crone is old enough that the distinction between her and the glacier she inhabits has become philosophically unclear.  The skin is ice-blue; the hair is actual frost that shifts with her movements; the eyes are white with no visible iris.  The magic she commands is pure cold in every application — she does not throw fire or lightning or energy, only cold in its various forms, which in her hands proves entirely sufficient."
return Creature
