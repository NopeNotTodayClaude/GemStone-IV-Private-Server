-- Creature: warped tree spirit
-- Zone: lunule_weald  |  Level: 16
-- Source: custom Lunule adaptation; kept in the Felwood band so the live zone
-- has a proper mid-tier plant threat instead of an empty creature shell.
local Creature = {}

Creature.id              = 9911
Creature.name            = "warped tree spirit"
Creature.level           = 16
Creature.family          = "plant"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 210
Creature.hp_variance     = 15

Creature.ds_melee        = 110
Creature.ds_bolt         = 105
Creature.td_spiritual    = 110
Creature.td_elemental    = 110
Creature.udf             = 95
Creature.armor_asg       = 7
Creature.armor_natural   = true

Creature.attacks = {
    { type = "slash", as = 172, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = { "entangle" }
Creature.immune    = {}
Creature.resist    = { "electricity" }

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a piece of corrupted bark"
Creature.special_loot = {}

Creature.decay_seconds  = 300
Creature.crumbles       = false
Creature.decay_message  = ""

Creature.spawn_rooms = {
    10559,
    10560,
    10561,
    10562,
    10563,
    10564,
    10565,
    10566,
    10567,
    10568,
    10569
}
Creature.roam_rooms  = {
    10559,
    10560,
    10561,
    10562,
    10563,
    10564,
    10565,
    10566,
    10567,
    10568,
    10569,
    10570,
    10571,
    10572,
    10573,
    10574,
    10575,
    10576,
    10577
}

Creature.roam_chance     = 10
Creature.respawn_seconds = 150
Creature.max_count       = 1

Creature.description = "A twisted amalgamation of living wood and dark magic.  What was once a noble tree spirit has been warped into something horrible and unnatural.  Its limbs writhe with corruption."

return Creature
