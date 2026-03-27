-- Creature: dark wisp
-- Zone: fethayl_bog  |  Level: 15
-- Source: https://gswiki.play.net/Dark_wisp
local Creature = {}

Creature.id              = 9913
Creature.name            = "dark wisp"
Creature.level           = 15
Creature.family          = "elemental"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 195
Creature.hp_variance     = 12

Creature.ds_melee        = 100
Creature.ds_bolt         = 95
Creature.td_spiritual    = 100
Creature.td_elemental    = 100
Creature.udf             = 80
Creature.armor_asg       = 1
Creature.armor_natural   = false

Creature.attacks = {
    { type = "gaze", as = 156, damage_type = "cold" },
}

Creature.spells    = {}
Creature.abilities = { "phase" }
Creature.immune    = { "cold", "electricity" }
Creature.resist    = {}

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = nil
Creature.special_loot = {}

Creature.decay_seconds  = 180
Creature.crumbles       = true
Creature.decay_message  = "The dark wisp collapses into a fading smear of cold light."

Creature.spawn_rooms = {}
Creature.roam_rooms  = {}

Creature.roam_chance     = 10
Creature.respawn_seconds = 180
Creature.max_count       = 3

Creature.description = "A swirling mass of dark energy coalescing into a vaguely humanoid shape.  Cold radiates off this creature in waves, and its eyes glow with an eerie blue light."

return Creature
