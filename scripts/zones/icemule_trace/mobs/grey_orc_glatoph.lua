-- Creature: grey orc
-- Zone: Icemule Trace / Glatoph  |  Level: 14
local Creature = {}
Creature.id              = 10307
Creature.name            = "grey orc"
Creature.level           = 14
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 178
Creature.hp_variance     = 14
Creature.ds_melee        = 120
Creature.ds_bolt         = 58
Creature.td_spiritual    = 46
Creature.td_elemental    = 46
Creature.udf             = 0
Creature.armor_asg       = 11
Creature.armor_natural   = false
Creature.attacks         = {
    { type="warhammer", as=172, damage_type="crush" },
    { type="longsword", as=166, damage_type="slash" },
}
Creature.spells          = {}
Creature.abilities       = {
    "battle_rage",
    "shield_bash",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "an orc beard"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    3678,
    3679,
    3680,
    3681,
    3682,
    4122,
    4123,
    4124,
    4125,
    4126,
    4127,
    4128,
    4129,
    4130,
    4131,
    4132,
    4133
    }
Creature.roam_rooms      = {
    3678,
    3679,
    3680,
    3681,
    3682,
    4122,
    4123,
    4124,
    4125,
    4126,
    4127,
    4128,
    4129,
    4130,
    4131,
    4132,
    4133,
    3553,
    3554,
    3559,
    3617
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 320
Creature.max_count       = 2
Creature.description     = "The grey orcs of Glatoph wear heavy furs over their standard armour, and the cold has done nothing to improve either their temperament or their fighting capability.  The ash-grey skin is here mottled with blue-grey from exposure, and the breath steams in the cold air — a constant reminder that these are living creatures that have adapted to brutal conditions."
return Creature
