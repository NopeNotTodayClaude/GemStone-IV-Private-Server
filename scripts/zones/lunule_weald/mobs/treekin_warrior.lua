-- Creature: treekin warrior
-- Zone: lunule_weald  |  Level: 17
-- Source: https://gswiki.play.net/Treekin_warrior
local Creature = {}

Creature.id              = 9912
Creature.name            = "treekin warrior"
Creature.level           = 17
Creature.family          = "plant"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 220
Creature.hp_variance     = 15

Creature.ds_melee        = 130
Creature.ds_bolt         = 120
Creature.td_spiritual    = 100
Creature.td_elemental    = 100
Creature.udf             = 130
Creature.armor_asg       = 8
Creature.armor_natural   = true

Creature.attacks = {
    { type = "slam",      as = 190, damage_type = "crush" },
    { type = "tail_sweep", as = 180, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = { "entangle", "thorn_armor" }
Creature.immune    = {}
Creature.resist    = { "electricity" }

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a treekin heartwood"
Creature.special_loot = {}

Creature.decay_seconds  = 300
Creature.crumbles       = false
Creature.decay_message  = ""

Creature.spawn_rooms = {}
Creature.roam_rooms  = {}

Creature.roam_chance     = 10
Creature.respawn_seconds = 180
Creature.max_count       = 3

Creature.description = "The treekin warrior is an imposing figure of living wood, standing over eight feet tall.  Unlike its lesser kin, this creature moves with deliberate, almost martial precision.  Thorny vines wrap around its limbs like armor, and it wields a massive club of petrified oak."

return Creature
