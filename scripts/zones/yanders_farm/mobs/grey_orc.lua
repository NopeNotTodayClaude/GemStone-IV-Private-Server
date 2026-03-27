-- Creature: grey orc
-- Zone: Yander's Farm / Corn & Barley Fields  |  Level: 14
local Creature = {}
Creature.id              = 9206
Creature.name            = "grey orc"
Creature.level           = 14
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 178
Creature.hp_variance     = 13
Creature.ds_melee        = 120
Creature.ds_bolt         = 58
Creature.td_spiritual    = 46
Creature.td_elemental    = 46
Creature.udf             = 0
Creature.armor_asg       = 11
Creature.armor_natural   = false
Creature.attacks = {
    { type="warhammer", as=172, damage_type="crush" },
    { type="longsword", as=166, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "battle_rage",
    "shield_bash",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "an orc ear"
Creature.special_loot = {
    "a grey orc war-token",
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
    6041,
    6042,
    6043,
    6044
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 320
Creature.max_count       = 3
Creature.description = "Ash-grey and broad as a doorframe, the grey orc stands at the upper end of orc physical development.  It carries a heavy weapon in each hand without apparent difficulty, and the crude shield strapped to one forearm has clearly deflected many blows.  The grey of its skin is deepened by years of grime and old blood that no amount of weather has managed to wash away."
return Creature
