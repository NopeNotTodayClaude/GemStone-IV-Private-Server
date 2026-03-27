-- Creature: dark orc
-- Zone: Yander's Farm / Corn Fields  |  Level: 12
local Creature = {}
Creature.id              = 9204
Creature.name            = "dark orc"
Creature.level           = 12
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 157
Creature.hp_variance     = 12
Creature.ds_melee        = 106
Creature.ds_bolt         = 52
Creature.td_spiritual    = 38
Creature.td_elemental    = 38
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false
Creature.attacks = {
    { type="longsword", as=156, damage_type="slash" },
    { type="military_pick", as=150, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {
    "battle_rage",
    "intimidating_presence",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "an orc ear"
Creature.special_loot = {
    "a dark orc warbrand",
}
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
    6059
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
Creature.roam_chance     = 18
Creature.respawn_seconds = 300
Creature.max_count       = 2
Creature.description = "Darker-skinned than typical orcs, with the deep charcoal-grey hide that gives them their name, dark orcs carry themselves with an aggressive confidence born of knowing they are among the toughest of their kind.  The armor they wear is better maintained than their lesser kin, and they fight with disciplined brutality rather than simple savagery."
return Creature
