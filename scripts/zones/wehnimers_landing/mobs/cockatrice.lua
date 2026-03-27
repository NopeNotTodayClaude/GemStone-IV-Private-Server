-- Creature: cockatrice
-- Zone: Upper Trollfang  |  Level: 6
local Creature = {}
Creature.id              = 9404
Creature.name            = "cockatrice"
Creature.level           = 6
Creature.family          = "cockatrice"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 88
Creature.hp_variance     = 8
Creature.ds_melee        = 70
Creature.ds_bolt         = 35
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 6
Creature.armor_asg       = 3
Creature.armor_natural   = true
Creature.attacks = {
    { type="peck", as=86, damage_type="puncture" },
    { type="claw", as=82, damage_type="slash" },
    { type="wing_buffet", as=78, damage_type="crush" },
}
Creature.spells = {
    { name="petrifying_gaze", cs=38, as=0 },
}
Creature.abilities = {
    "petrify_gaze",
    "paralytic_saliva",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a cockatrice feather"
Creature.special_loot = {
    "a cockatrice comb",
}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
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
    1216,
    470,
    471,
    472,
    473,
    474,
    475
    }
Creature.roam_rooms = {
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
    1216,
    470,
    471,
    472,
    473,
    474,
    475
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 4
Creature.description = "Part serpent and part rooster, the cockatrice is an improbable nightmare of natural history.  Scaled legs end in powerful talons, a cock's comb of vivid scarlet surmounts a flat, reptilian head, and vestigial wings spread when it is alarmed or aggressive.  The gaze of its golden eyes is said to have petrifying properties, and the paralytic quality of its beak and talons is well-documented."
return Creature
