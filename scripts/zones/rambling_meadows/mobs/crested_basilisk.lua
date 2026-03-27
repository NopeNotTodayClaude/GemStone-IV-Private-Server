-- Creature: crested basilisk
-- Zone: Rambling Meadows / Hilltop  |  Level: 22
local Creature = {}

Creature.id              = 9111
Creature.name            = "crested basilisk"
Creature.level           = 22
Creature.family          = "basilisk"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 268
Creature.hp_variance     = 20

Creature.ds_melee        = 202
Creature.ds_bolt         = 95
Creature.td_spiritual    = 70
Creature.td_elemental    = 70
Creature.udf             = 12
Creature.armor_asg       = 11
Creature.armor_natural   = true

Creature.attacks = {
    { type="bite", as=238, damage_type="puncture" },
    { type="claw", as=232, damage_type="slash" },
    { type="tail_sweep", as=225, damage_type="crush" },
}
Creature.spells = {
    { name="petrifying_gaze", cs=115, as=0 },
}
Creature.abilities = {
    "petrify_gaze",
    "stone_skin",
    "paralyzing_bite",
}
Creature.immune    = {
    "poison",
}
Creature.resist    = {
    "cold",
    "fire",
}

Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = "a basilisk scale"
Creature.special_loot = {
    "a basilisk eye",
}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    6002,
    6003,
    6004,
    6005,
    6006,
    6007,
    6008,
    6009
    }
Creature.roam_rooms = {
    6002,
    6003,
    6004,
    6005,
    6006,
    6007,
    6008,
    6009
    }

Creature.roam_chance     = 8
Creature.respawn_seconds = 600
Creature.max_count       = 1

Creature.description = "Eight-legged, low-slung, and covered in overlapping bony plates edged with a vivid blood-red crest along the spine and tail, the crested basilisk is genuinely disturbing to look upon.  Its eyes — compound and multifaceted, gleaming with an inner violet light — are said to have the power to stop a warrior in their tracks.  The hilltop it claims shows evidence of long occupation, littered with the stone-grey remnants of the incautious."

return Creature
