-- Creature: great stag
-- Zone: Yander's Farm / Corn Fields  |  Level: 13
local Creature = {}
Creature.id              = 9205
Creature.name            = "great stag"
Creature.level           = 13
Creature.family          = "deer"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 168
Creature.hp_variance     = 12
Creature.ds_melee        = 118
Creature.ds_bolt         = 55
Creature.td_spiritual    = 42
Creature.td_elemental    = 42
Creature.udf             = 5
Creature.armor_asg       = 2
Creature.armor_natural   = true
Creature.attacks = {
    { type="gore", as=162, damage_type="puncture" },
    { type="kick", as=156, damage_type="crush" },
    { type="charge", as=152, damage_type="crush" },
}
Creature.spells = {}
Creature.abilities = {
    "antler_sweep",
    "powerful_kick",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "antlers"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    6045,
    6046,
    6047,
    6048,
    6049,
    6050,
    6051,
    6052,
    6053,
    6054,
    6055,
    6056,
    6057,
    6058,
    6059,
    6068,
    6069,
    6070,
    6071,
    6072,
    10261
    }
Creature.roam_rooms = {
    6045,
    6046,
    6047,
    6048,
    6049,
    6050,
    6051,
    6052,
    6053,
    6054,
    6055,
    6056,
    6057,
    6058,
    6059,
    6068,
    6069,
    6070,
    6071,
    6072,
    10261,
    6024,
    6041,
    6042,
    6043,
    6044
    }
Creature.roam_chance     = 22
Creature.respawn_seconds = 300
Creature.max_count       = 3
Creature.description = "An immense specimen of a red deer, the great stag carries a rack of antlers so massive they seem almost architectural.  A thick neck and deep chest support a body the size of a small horse, and when it wheels to face you the sheer weight behind those antlers becomes immediately concerning.  The rut has made it almost recklessly aggressive."
return Creature
