-- Creature: warclaw
-- Zone: grasslands  |  Level: 13
-- Source: https://gswiki.play.net/Warclaw
local Creature = {}

Creature.id              = 9914
Creature.name            = "warclaw"
Creature.level           = 13
Creature.family          = "beast"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 170
Creature.hp_variance     = 12

Creature.ds_melee        = 88
Creature.ds_bolt         = 82
Creature.td_spiritual    = 90
Creature.td_elemental    = 90
Creature.udf             = 70
Creature.armor_asg       = 6
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw", as = 140, damage_type = "slash" },
    { type = "bite", as = 135, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = { "pounce" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = "a warclaw pelt"
Creature.special_loot = {}

Creature.decay_seconds  = 300
Creature.crumbles       = false
Creature.decay_message  = ""

Creature.spawn_rooms = {}
Creature.roam_rooms  = {}

Creature.roam_chance     = 20
Creature.respawn_seconds = 180
Creature.max_count       = 3

Creature.description = "A large predatory creature resembling a cross between a big cat and a reptile.  Its scaled hide ripples with movement, and its claws look wickedly sharp."

return Creature
