-- Creature: wood sprite
-- Zone: lunule_weald  |  Level: 7
-- Source: https://gswiki.play.net/Wood_sprite
local Creature = {}

Creature.id              = 9910
Creature.name            = "wood sprite"
Creature.level           = 7
Creature.family          = "plant"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 95
Creature.hp_variance     = 8

Creature.ds_melee        = 54
Creature.ds_bolt         = 50
Creature.td_spiritual    = 50
Creature.td_elemental    = 50
Creature.udf             = 40
Creature.armor_asg       = 4
Creature.armor_natural   = true

Creature.attacks = {
    { type = "swipe", as = 88, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = { "electricity" }

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = nil
Creature.special_loot = {}

Creature.decay_seconds  = 300
Creature.crumbles       = false
Creature.decay_message  = ""

-- Spawn rooms assigned when Lunule Weald hunting areas are finalised.
Creature.spawn_rooms = {}
Creature.roam_rooms  = {}

Creature.roam_chance     = 15
Creature.respawn_seconds = 120
Creature.max_count       = 3

Creature.description = "A lithe, ethereal creature made of living wood and vines.  Its form is vaguely humanoid, with glowing eyes that shimmer with ancient magic."

return Creature
