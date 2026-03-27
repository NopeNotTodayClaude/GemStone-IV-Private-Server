-- Creature: grey orc
-- Zone: Upper Trollfang / Lower  |  Level: 14
local Creature = {}
Creature.id              = 9411
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
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    7155,
    7156,
    7157,
    7158,
    7159,
    7160,
    7161,
    7162
    }
Creature.roam_rooms = {
    7155,
    7156,
    7157,
    7158,
    7159,
    7160,
    7161,
    7162,
    4115,
    4116,
    4117
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 320
Creature.max_count       = 1
Creature.description = "Ash-grey skinned and broad-shouldered even by orc standards, the grey orc of the trollfang has been hardened by proximity to trolls and worse things deeper in the hills.  The armor it wears is better quality than its lesser kin — some of it clearly looted from adventurers who came this way and did not leave — and it fights with grim, patient experience."
return Creature
