-- Creature: greater orc
-- Zone: Upper Trollfang / Swamp  |  Level: 8
local Creature = {}
Creature.id              = 9405
Creature.name            = "greater orc"
Creature.level           = 8
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 115
Creature.hp_variance     = 9
Creature.ds_melee        = 80
Creature.ds_bolt         = 38
Creature.td_spiritual    = 25
Creature.td_elemental    = 25
Creature.udf             = 0
Creature.armor_asg       = 9
Creature.armor_natural   = false
Creature.attacks = {
    { type="morning_star", as=112, damage_type="crush" },
    { type="shortsword", as=106, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "battle_fury",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "an orc ear"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    4106,
    4107,
    4108,
    4109,
    4110,
    4111,
    4112,
    4113,
    4114,
    4115,
    4116,
    4117,
    1212,
    1213,
    1214,
    1215,
    1216
    }
Creature.roam_rooms = {
    4106,
    4107,
    4108,
    4109,
    4110,
    4111,
    4112,
    4113,
    4114,
    4115,
    4116,
    4117,
    1212,
    1213,
    1214,
    1215,
    1216,
    472,
    473,
    474,
    475
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 260
Creature.max_count       = 2
Creature.description = "Substantially larger than its lesser kin, the greater orc has the look of a creature that has survived a great deal of violence and come out ahead every time.  Heavy scarring crosses its grey-green hide, and the weapons it carries bear the nicks and stains of extensive use.  It fights with a methodical brutality — no wasted motion, maximum damage."
return Creature
