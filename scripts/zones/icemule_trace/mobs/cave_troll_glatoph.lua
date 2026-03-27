-- Creature: cave troll
-- Zone: Icemule Trace / Glatoph  |  Level: 16
local Creature = {}
Creature.id              = 10311
Creature.name            = "cave troll"
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
    "cave_sight",
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
    7835,
    7836,
    7837,
    7838,
    7839,
    7840,
    7841,
    7842,
    7843,
    7844,
    7845,
    7846,
    7847,
    7848,
    7849,
    7850
    }
Creature.roam_rooms      = {
    7835,
    7836,
    7837,
    7838,
    7839,
    7840,
    7841,
    7842,
    7843,
    7844,
    7845,
    7846,
    7847,
    7848,
    7849,
    7850
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 360
Creature.max_count       = 2
Creature.description     = "The pale, large-eyed cave troll of the Glatoph glacial tunnels. The enormous eyes give excellent low-light vision, and the long arms are suited to the cramped passages it navigates. The cold that permeates its home territory has bleached the skin to near-white, and the regenerative capability keeps it operational regardless of what you do to it until fire becomes involved."
return Creature
