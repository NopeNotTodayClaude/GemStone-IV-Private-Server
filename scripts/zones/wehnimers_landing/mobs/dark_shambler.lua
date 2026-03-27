-- Creature: dark shambler
-- Zone: Upper Trollfang / Sentoph  |  Level: 17
local Creature = {}
Creature.id              = 9414
Creature.name            = "dark shambler"
Creature.level           = 17
Creature.family          = "shambler"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 210
Creature.hp_variance     = 15
Creature.ds_melee        = 148
Creature.ds_bolt         = 72
Creature.td_spiritual    = 56
Creature.td_elemental    = 56
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false
Creature.attacks = {
    { type="claw", as=198, damage_type="slash" },
    { type="bite", as=192, damage_type="puncture" },
    { type="pound", as=185, damage_type="crush" },
}
Creature.spells = {}
Creature.abilities = {
    "disease_touch",
    "sulfurous_appearance",
    "toxic_bite",
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
Creature.skin        = "a shambler hide"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    6821,
    6822,
    6823,
    6824,
    6825,
    6826,
    6827,
    6828,
    6829,
    6830,
    6831,
    6832,
    6833,
    6834,
    6835
    }
Creature.roam_rooms = {
    6821,
    6822,
    6823,
    6824,
    6825,
    6826,
    6827,
    6828,
    6829,
    6830,
    6831,
    6832,
    6833,
    6834,
    6835,
    7786,
    7787,
    7788
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 420
Creature.max_count       = 2
Creature.description = "The dark shambler moves with the artless, lurching gait of something whose construction has gone badly wrong.  Thick-limbed and wrong-proportioned, with a hunched back and arms that nearly touch the ground, it leaves a faint trail of sulphurous smoke wherever it passes.  The skin is blackened and cracked like cooling lava, and a sickly bioluminescence pulses faintly in the crevices."
return Creature
