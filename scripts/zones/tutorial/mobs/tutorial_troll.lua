-- Creature: cave troll (tutorial)
-- Zone: tutorial  |  Level: 2
-- Scripted tutorial encounter — not a wild spawn.
local Creature = {}

Creature.id              = 9902
Creature.name            = "cave troll"
Creature.level           = 2
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 40
Creature.hp_variance     = 0

Creature.ds_melee        = 15
Creature.ds_bolt         = 10
Creature.td_spiritual    = 5
Creature.td_elemental    = 5
Creature.udf             = 10
Creature.armor_asg       = 3
Creature.armor_natural   = true

Creature.attacks = {
    { type = "slam",  as = 45, damage_type = "crush" },
    { type = "claw",  as = 40, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a piece of troll skin"
Creature.special_loot = {}

Creature.decay_seconds  = 180
Creature.crumbles       = false
Creature.decay_message  = ""

Creature.spawn_rooms = { 59052 }
Creature.roam_rooms  = { 59052 }

Creature.roam_chance     = 0
Creature.respawn_seconds = 9999
Creature.max_count       = 1

Creature.description = "A hulking cave troll fills much of the chamber, its warty grey-green hide scarred from countless underground skirmishes.  Beady eyes peer from beneath a heavy brow, and its breath is absolutely foul."

return Creature
