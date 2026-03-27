-- Creature: lesser orc
-- Zone: Upper Trollfang / Upper  |  Level: 6
local Creature = {}
Creature.id              = 9403
Creature.name            = "lesser orc"
Creature.level           = 6
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 90
Creature.hp_variance     = 8
Creature.ds_melee        = 64
Creature.ds_bolt         = 30
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 0
Creature.armor_asg       = 7
Creature.armor_natural   = false
Creature.attacks = {
    { type="handaxe", as=88, damage_type="slash" },
    { type="shortsword", as=84, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {}
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
    452,
    453,
    454,
    455,
    456,
    457,
    458,
    459,
    460,
    461,
    462,
    463,
    464,
    465,
    466,
    467,
    468,
    469,
    470,
    471,
    472,
    473,
    474,
    475,
    1196,
    1197,
    1198,
    1199,
    1200,
    1201,
    1202,
    1203
    }
Creature.roam_rooms = {
    452,
    453,
    454,
    455,
    456,
    457,
    458,
    459,
    460,
    461,
    462,
    463,
    464,
    465,
    466,
    467,
    468,
    469,
    470,
    471,
    472,
    473,
    474,
    475,
    1196,
    1197,
    1198,
    1199,
    1200,
    1201,
    1202,
    1203,
    1204,
    1205,
    1206,
    1207,
    1208,
    1209,
    1210,
    1211,
    1212,
    1213,
    1214,
    1215,
    1216
    }
Creature.roam_chance     = 22
Creature.respawn_seconds = 240
Creature.max_count       = 4
Creature.description = "Barely larger than a human but twice as belligerent, the lesser orc makes up for what it lacks in size with relentless aggression.  Rough-hewn weapons, mismatched armor, and a permanent sneer complete the picture.  Lesser orcs patrol the upper trollfang in loose groups, willing to attack virtually anything that enters their loosely-defined territory."
return Creature
