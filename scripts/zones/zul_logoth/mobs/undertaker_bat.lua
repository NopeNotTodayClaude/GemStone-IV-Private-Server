-- Creature: undertaker bat
-- Zone: Zul Logoth / Troll Burial Grounds  |  Level: 36
local Creature = {}
Creature.id              = 10406
Creature.name            = "undertaker bat"
Creature.level           = 36
Creature.family          = "bat"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 455
Creature.hp_variance     = 37
Creature.ds_melee        = 292
Creature.ds_bolt         = 145
Creature.td_spiritual    = 116
Creature.td_elemental    = 116
Creature.udf             = 8
Creature.armor_asg       = 4
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=448, damage_type="puncture" },
    { type="claw", as=440, damage_type="slash" },
    { type="wing_buffet", as=432, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "echolocation",
    "diving_strike",
    "disease_bite",
    "blindness_immunity",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "an undertaker bat wing membrane"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    5752,
    5753,
    5754,
    5756,
    5757,
    5758,
    5759,
    5760,
    5761,
    5762,
    5763,
    5764,
    5770,
    5771,
    5772,
    5773,
    5774,
    5775,
    5818,
    5819,
    5820,
    5821,
    5822
    }
Creature.roam_rooms      = {
    5752,
    5753,
    5754,
    5756,
    5757,
    5758,
    5759,
    5760,
    5761,
    5762,
    5763,
    5764,
    5770,
    5771,
    5772,
    5773,
    5774,
    5775,
    5818,
    5819,
    5820,
    5821,
    5822
    }
Creature.roam_chance     = 25
Creature.respawn_seconds = 480
Creature.max_count       = 3
Creature.description     = "Named for its habit of circling areas where creatures have recently died, the undertaker bat is large enough to carry away a young rolton.  The wingspan exceeds ten feet, and the echolocation it uses is so precise it can navigate in absolute darkness at full speed.  The disease carried in the bite is a secondary concern to the initial trauma, but both are problems that tend to compound."
return Creature
