-- Creature: war troll
-- Zone: Icemule Trace / Glatoph  |  Level: 18
local Creature = {}
Creature.id              = 10310
Creature.name            = "war troll"
Creature.level           = 18
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 222
Creature.hp_variance     = 18
Creature.ds_melee        = 158
Creature.ds_bolt         = 75
Creature.td_spiritual    = 57
Creature.td_elemental    = 57
Creature.udf             = 0
Creature.armor_asg       = 11
Creature.armor_natural   = false
Creature.attacks         = {
    { type="waraxe", as=218, damage_type="slash" },
    { type="claw", as=210, damage_type="slash" },
    { type="pound", as=202, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "troll_regeneration",
    "battle_fury",
    "rend",
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
    7821,
    7824,
    7825,
    7826,
    7827,
    7828,
    7829,
    7830,
    7831,
    7832,
    7833,
    7834,
    7835,
    7836,
    7837,
    7838,
    7839,
    7840
    }
Creature.roam_rooms      = {
    7821,
    7824,
    7825,
    7826,
    7827,
    7828,
    7829,
    7830,
    7831,
    7832,
    7833,
    7834,
    7835,
    7836,
    7837,
    7838,
    7839,
    7840
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 380
Creature.max_count       = 2
Creature.description     = "A war troll has been specifically raised and trained for combat — which mostly means it has been starved and beaten until fighting is its default response to any stimulus.  The crude armour it wears has been fitted to it rather than scavenged, and the waraxe it carries shows actual edge maintenance.  The training has not made it faster or smarter, but it has made it relentless in a way that even other trolls are not."
return Creature
