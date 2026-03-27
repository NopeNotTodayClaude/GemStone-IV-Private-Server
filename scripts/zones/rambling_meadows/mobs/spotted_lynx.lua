-- Creature: spotted lynx
-- Zone: Rambling Meadows  |  Level: 6
local Creature = {}

Creature.id              = 9109
Creature.name            = "spotted lynx"
Creature.level           = 6
Creature.family          = "feline"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 86
Creature.hp_variance     = 8

Creature.ds_melee        = 68
Creature.ds_bolt         = 32
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 5
Creature.armor_asg       = 2
Creature.armor_natural   = true

Creature.attacks = {
    { type="claw", as=88, damage_type="slash" },
    { type="bite", as=82, damage_type="puncture" },
    { type="rake", as=78, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "pounce_maneuver",
    "stealth_ambush",
}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a lynx pelt"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    5995,
    5996,
    5997,
    5998,
    5999,
    6000,
    6001,
    6002,
    6003,
    6004,
    6005,
    6006,
    6007,
    6008,
    6009,
    6027,
    6028,
    6029,
    6030
    }
Creature.roam_rooms = {
    5995,
    5996,
    5997,
    5998,
    5999,
    6000,
    6001,
    6002,
    6003,
    6004,
    6005,
    6006,
    6007,
    6008,
    6009,
    5991,
    5992,
    5993,
    6027,
    6028,
    6029,
    6030
    }

Creature.roam_chance     = 25
Creature.respawn_seconds = 240
Creature.max_count       = 2

Creature.description = "Tufted ears erect, the spotted lynx crouches at the hilltop's edge and watches the terrain below with patient calculation.  Its coat is a dense, spotted grey-buff perfectly suited to the rocky hillside, and the broad paws that carry it are silent on any surface.  Despite its compact frame it can cover enormous distance in a single bound."

return Creature
