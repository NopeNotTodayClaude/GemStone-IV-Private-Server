-- Creature: rotting farmhand
-- Zone: Lunule Weald / Slade  |  Level: 13
local Creature = {}
Creature.id              = 9501
Creature.name            = "rotting farmhand"
Creature.level           = 13
Creature.family          = "zombie"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 165
Creature.hp_variance     = 12
Creature.ds_melee        = 110
Creature.ds_bolt         = 52
Creature.td_spiritual    = 44
Creature.td_elemental    = 44
Creature.udf             = 145
Creature.armor_asg       = 5
Creature.armor_natural   = false
Creature.attacks = {
    { type="claw", as=163, damage_type="slash" },
    { type="bite", as=156, damage_type="puncture" },
    { type="pound", as=150, damage_type="crush" },
}
Creature.spells = {}
Creature.abilities = {
    "disease_touch",
    "shambling_gait",
}
Creature.immune    = {
    "disease",
    "poison",
}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a zombie hand"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    10540,
    10541,
    10542,
    10543,
    10544,
    10548,
    10549,
    10550,
    10551,
    10556,
    10557,
    10558
    }
Creature.roam_rooms = {
    10540,
    10541,
    10542,
    10543,
    10544,
    10548,
    10549,
    10550,
    10551,
    10556,
    10557,
    10558,
    10545,
    10546
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 320
Creature.max_count       = 1
Creature.description = "Whatever this farmhand was in life has been stripped away by the corrupting influence of the Weald.  What remains wears the rotted remnants of working clothes and shambles through the Slade as though still dimly aware of chores left undone.  The jaw hangs loose; the eyes are a uniform, lightless black.  The smell arrives well before the creature does."
return Creature
