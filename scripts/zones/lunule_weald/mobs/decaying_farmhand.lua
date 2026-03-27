-- Creature: decaying farmhand
-- Zone: Lunule Weald / Slade  |  Level: 14
local Creature = {}
Creature.id              = 9502
Creature.name            = "decaying farmhand"
Creature.level           = 14
Creature.family          = "zombie"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 176
Creature.hp_variance     = 13
Creature.ds_melee        = 120
Creature.ds_bolt         = 56
Creature.td_spiritual    = 47
Creature.td_elemental    = 47
Creature.udf             = 155
Creature.armor_asg       = 5
Creature.armor_natural   = false
Creature.attacks = {
    { type="claw", as=172, damage_type="slash" },
    { type="bite", as=165, damage_type="puncture" },
    { type="pound", as=158, damage_type="crush" },
}
Creature.spells = {}
Creature.abilities = {
    "disease_touch",
    "shambling_gait",
    "infectious_bite",
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
    10558,
    10545,
    10546
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
    10546,
    10552,
    10553,
    10554,
    10555
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 340
Creature.max_count       = 2
Creature.description = "Further along in the process of decay than its lesser counterpart, the decaying farmhand has sloughed away enough flesh to reveal the yellow-grey bone beneath in patches.  The animation that drives it is somehow more insistent than in a fresher corpse — the lurching movements are more deliberate, the jaw works with a grinding rhythm, and it tracks living creatures with blank, absolute focus."
return Creature
