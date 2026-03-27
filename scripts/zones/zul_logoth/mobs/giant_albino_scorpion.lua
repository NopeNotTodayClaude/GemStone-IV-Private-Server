-- Creature: giant albino scorpion
-- Zone: Zul Logoth / Mraent Cavern  |  Level: 24
local Creature = {}
Creature.id              = 10407
Creature.name            = "giant albino scorpion"
Creature.level           = 24
Creature.family          = "scorpion"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 295
Creature.hp_variance     = 24
Creature.ds_melee        = 205
Creature.ds_bolt         = 100
Creature.td_spiritual    = 76
Creature.td_elemental    = 76
Creature.udf             = 8
Creature.armor_asg       = 12
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=290, damage_type="slash" },
    { type="sting", as=282, damage_type="puncture" },
    { type="venom_sting", as=275, damage_type="puncture" },
}
Creature.spells          = {}
Creature.abilities       = {
    "venom_sting",
    "armoured_carapace",
    "blindness_immunity",
    "tunnel_sight",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a scorpion carapace plate"
Creature.special_loot    = {
    "a scorpion venom sac",
}
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
    5776,
    5777,
    5778,
    5779,
    5780,
    5781,
    9459,
    9460,
    9461,
    9462,
    9463,
    9464,
    9465,
    9466,
    9467,
    9468
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
    5776,
    5777,
    5778,
    5779,
    5780,
    5781,
    9459,
    9460,
    9461,
    9462,
    9463,
    9464,
    9465,
    9466,
    9467,
    9468
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 420
Creature.max_count       = 4
Creature.description     = "Albino from generations of cave-dwelling and large enough that the pincers can grip a human torso, the giant albino scorpion is the apex predator of Mraent Cavern.  The exoskeleton is utterly white with a faint translucency that lets the internal structure show in good light.  The venom in the tail stinger induces progressive paralysis; the claws are purely mechanical and require no special properties to be alarming."
return Creature
