-- Creature: wood sprite
-- Zone: lunule_weald  |  Level: 13
-- Source: custom Lunule adaptation; balanced to the Slade/Knoll band so the
-- creature sits cleanly with the other early Weald creatures.
local Creature = {}

Creature.id              = 9910
Creature.name            = "wood sprite"
Creature.level           = 13
Creature.family          = "plant"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 152
Creature.hp_variance     = 12

Creature.ds_melee        = 98
Creature.ds_bolt         = 54
Creature.td_spiritual    = 44
Creature.td_elemental    = 44
Creature.udf             = 118
Creature.armor_asg       = 5
Creature.armor_natural   = true

Creature.attacks = {
    { type = "swipe", as = 154, damage_type = "slash" },
    { type = "vine_whip", as = 148, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = { "entangle" }
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

Creature.spawn_rooms = {
    10540,
    10541,
    10542,
    10543,
    10544,
    10545,
    10546,
    10548,
    10549,
    10550,
    10551,
    10552,
    10553,
    10554,
    10555,
    10556,
    10557,
    10558
}
Creature.roam_rooms  = {
    10540,
    10541,
    10542,
    10543,
    10544,
    10545,
    10546,
    10547,
    10548,
    10549,
    10550,
    10551,
    10552,
    10553,
    10554,
    10555,
    10556,
    10557,
    10558,
    10559,
    10560
}

Creature.roam_chance     = 15
Creature.respawn_seconds = 300
Creature.max_count       = 1

Creature.description = "A lithe, ethereal creature made of living wood and vines.  Its form is vaguely humanoid, with glowing eyes that shimmer with ancient magic."

return Creature
