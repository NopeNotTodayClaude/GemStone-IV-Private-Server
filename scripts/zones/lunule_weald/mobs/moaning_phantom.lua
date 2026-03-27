-- Creature: moaning phantom
-- Zone: Lunule Weald / Perish Glen  |  Level: 20
local Creature = {}
Creature.id              = 9508
Creature.name            = "moaning phantom"
Creature.level           = 20
Creature.family          = "phantom"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 230
Creature.hp_variance     = 16
Creature.ds_melee        = 170
Creature.ds_bolt         = 80
Creature.td_spiritual    = 65
Creature.td_elemental    = 45
Creature.udf             = 242
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks = {
    { type="spectral_touch", as=215, damage_type="unbalancing" },
    { type="despair_wave", as=208, damage_type="unbalancing" },
}
Creature.spells = {
    { name="despair", cs=115, as=0 },
    { name="phantasmal_fear", cs=110, as=0 },
}
Creature.abilities = {
    "spirit_strike",
    "despair_aura",
    "phase_through_terrain",
    "fear_aura",
}
Creature.immune    = {
    "disease",
    "poison",
    "cold",
}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = ""
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = "disperses with a final shuddering moan."
Creature.spawn_rooms = {
    10583,
    10584,
    10585,
    10586,
    10587,
    10588,
    10589,
    10590,
    10591,
    10592
    }
Creature.roam_rooms = {
    10578,
    10579,
    10580,
    10581,
    10582,
    10583,
    10584,
    10585,
    10586,
    10587,
    10588,
    10589,
    10590,
    10591,
    10592,
    10593,
    10594,
    10595,
    10610
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 480
Creature.max_count       = 2
Creature.description = "The moaning phantom makes its misery known at considerable distance — a low, sustained moan that carries through the dead wood of Perish Glen with the directional quality of a voice rather than random sound.  It appears as a human-shaped luminescence of pale blue-grey, features recognizable but distorted by whatever torment anchors it here.  The despair it radiates is not metaphorical; proximity has been documented to sap the will to fight."
return Creature
