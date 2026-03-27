-- Creature: scaly burgee
-- Zone: Teras Isle / Basalt Flats Beach  |  Level: 29
local Creature = {}
Creature.id              = 10205
Creature.name            = "scaly burgee"
Creature.level           = 29
Creature.family          = "lizard"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 358
Creature.hp_variance     = 29
Creature.ds_melee        = 242
Creature.ds_bolt         = 118
Creature.td_spiritual    = 92
Creature.td_elemental    = 92
Creature.udf             = 8
Creature.armor_asg       = 10
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=350, damage_type="puncture" },
    { type="claw", as=342, damage_type="slash" },
    { type="tail_sweep", as=335, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "armoured_scales",
    "tail_sweep",
    "fast_reflexes",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a burgee scale"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    12575,
    12576,
    12577,
    12578
    }
Creature.roam_rooms      = {
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    12575,
    12576,
    12577,
    12578
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 480
Creature.max_count       = 2
Creature.description     = "The scaly burgee is a large, quadrupedal lizard native to the volcanic beaches of Teras Isle, where its dark grey-brown scaling blends perfectly with the basalt.  It moves in short bursts of speed between long periods of absolute stillness, a hunting strategy that has proven remarkably effective against prey that mistakes it for an oddly-shaped rock.  The tail can deliver a striking blow."
return Creature
