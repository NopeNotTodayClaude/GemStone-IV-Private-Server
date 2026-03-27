-- Creature: lesser red orc
-- Zone: Yander's Farm / Turnip Patch  |  Level: 7
local Creature = {}

Creature.id              = 9110
Creature.name            = "lesser red orc"
Creature.level           = 7
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 98
Creature.hp_variance     = 8

Creature.ds_melee        = 64
Creature.ds_bolt         = 32
Creature.td_spiritual    = 21
Creature.td_elemental    = 21
Creature.udf             = 0
Creature.armor_asg       = 8
Creature.armor_natural   = false

Creature.attacks = {
    { type="handaxe", as=100, damage_type="slash" },
    { type="spear", as=96, damage_type="puncture" },
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
    6032,
    6033,
    6034,
    6035,
    6036,
    6037,
    6038,
    6039,
    6040
}
Creature.roam_rooms = {
    6024,
    6027,
    6028,
    6029,
    6030,
    6031,
    6032,
    6033,
    6034,
    6035,
    6036,
    6037,
    6038,
    6039,
    6040,
    6041,
    6042,
    6043,
    6044
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 260
Creature.max_count       = 2

Creature.description = "Shorter than its larger kin but no less aggressive, the lesser red orc has the characteristic rust-red skin and jutting lower jaw of its tribe.  Scarification marks cover its arms and face in patterns of tribal significance, and it carries crude weapons with the casual confidence of something accustomed to using them."

return Creature
