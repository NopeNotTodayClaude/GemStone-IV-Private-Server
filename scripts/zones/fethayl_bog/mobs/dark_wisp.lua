-- Creature: dark wisp
-- Zone: fethayl_bog  |  Level: 45
-- Source: no clean retail bestiary page found in current audit; balanced between
-- bog wight (44) and bog spectre (47) so the creature fits the live Fethayl range.
local Creature = {}

Creature.id              = 9913
Creature.name            = "dark wisp"
Creature.level           = 45
Creature.family          = "elemental"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 515
Creature.hp_variance     = 28

Creature.ds_melee        = 286
Creature.ds_bolt         = 148
Creature.td_spiritual    = 152
Creature.td_elemental    = 152
Creature.udf             = 298
Creature.armor_asg       = 1
Creature.armor_natural   = false

Creature.attacks = {
    { type = "gaze", as = 438, damage_type = "cold" },
    { type = "shockwave", as = 430, damage_type = "unbalancing" },
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

Creature.spawn_rooms = {
    10130,
    10131,
    10132,
    10133,
    10134,
    10135,
    10136,
    10137,
    10138,
    10139,
    10140,
    10141,
    10142,
    10143,
    10144,
    10145,
    10146
}
Creature.roam_rooms  = {
    10130,
    10131,
    10132,
    10133,
    10134,
    10135,
    10136,
    10137,
    10138,
    10139,
    10140,
    10141,
    10142,
    10143,
    10144,
    10145,
    10146,
    10147,
    10148,
    10149,
    10150,
    10151,
    10152
}

Creature.roam_chance     = 10
Creature.respawn_seconds = 540
Creature.max_count       = 1

Creature.description = "A swirling mass of dark energy coalescing into a vaguely humanoid shape.  Cold radiates off this creature in waves, and its eyes glow with an eerie blue light."

return Creature
