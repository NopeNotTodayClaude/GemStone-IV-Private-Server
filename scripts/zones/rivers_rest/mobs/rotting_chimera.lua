-- Creature: rotting chimera
-- Zone: Marsh Keep  |  Level: 46
local Creature = {}
Creature.id              = 10015
Creature.name            = "rotting chimera"
Creature.level           = 46
Creature.family          = "chimera"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "quadruped"
Creature.hp_base         = 562
Creature.hp_variance     = 46
Creature.ds_melee        = 360
Creature.ds_bolt         = 182
Creature.td_spiritual    = 152
Creature.td_elemental    = 152
Creature.udf             = 365
Creature.armor_asg       = 12
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite_lion", as=442, damage_type="puncture" },
    { type="gore_goat", as=434, damage_type="puncture" },
    { type="tail_sting", as=428, damage_type="puncture" },
    { type="claw", as=420, damage_type="slash" },
}
Creature.spells          = {
    { name="necrotic_breath", cs=232, as=0 },
}
Creature.abilities       = {
    "multi_attack",
    "disease_touch",
    "necrotic_breath",
    "undead_resilience",
}
Creature.immune          = {
    "disease",
    "poison",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a chimera scale"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11711,
    11712,
    11713,
    11714,
    11715,
    11716,
    11717,
    11718,
    11719,
    11720,
    11721,
    11722,
    11723,
    11724,
    11725,
    11726,
    11727,
    11728,
    11729,
    11730
    }
Creature.roam_rooms      = {
    11711,
    11712,
    11713,
    11714,
    11715,
    11716,
    11717,
    11718,
    11719,
    11720,
    11721,
    11722,
    11723,
    11724,
    11725,
    11726,
    11727,
    11728,
    11729,
    11730
    }
Creature.roam_chance     = 8
Creature.respawn_seconds = 660
Creature.max_count       = 3
Creature.description     = "The rotting chimera is what remains of a creature already bizarre in life: the three-headed hybrid of lion, goat, and serpent, now animated in undeath with the lion's head carrying the goat's horns as well as its own fangs, and the serpent tail sporting a venomous spur of bone.  Decay has not stopped any of these weapons from functioning.  The necrotic exhalation from all three mouths is perhaps the most immediately threatening feature."
return Creature
