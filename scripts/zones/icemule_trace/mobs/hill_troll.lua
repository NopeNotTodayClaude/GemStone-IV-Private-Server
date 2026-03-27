-- Creature: hill troll
-- Zone: Icemule Trace / Glatoph  |  Level: 16
local Creature = {}
Creature.id              = 10309
Creature.name            = "hill troll"
Creature.level           = 16
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 200
Creature.hp_variance     = 16
Creature.ds_melee        = 140
Creature.ds_bolt         = 66
Creature.td_spiritual    = 51
Creature.td_elemental    = 51
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=196, damage_type="slash" },
    { type="bite", as=188, damage_type="puncture" },
    { type="pound", as=182, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "troll_regeneration",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a troll scalp"
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
    4133,
    7821,
    7824,
    7825,
    7826,
    7827,
    7828,
    7829,
    7830
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
    7821,
    7824,
    7825,
    7826,
    7827,
    7828,
    7829,
    7830
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 360
Creature.max_count       = 3
Creature.description     = "The hill troll is the standard-issue troll of the Glatoph slopes — broad, belligerent, and regenerating wounds at a pace that rewards finishing the job quickly.  The skin has the grey-brown tones common to highland trolls, and the face carries the perpetual scowl of a creature that has just found out the weather is going to get worse.  Which it generally is."
return Creature
