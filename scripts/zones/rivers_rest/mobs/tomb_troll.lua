-- Creature: Tomb Troll
-- Zone: Marsh Keep  |  Level: 52
local Creature = {}
Creature.id              = 10018
Creature.name            = "Tomb Troll"
Creature.level           = 52
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 625
Creature.hp_variance     = 52
Creature.ds_melee        = 395
Creature.ds_bolt         = 198
Creature.td_spiritual    = 168
Creature.td_elemental    = 168
Creature.udf             = 0
Creature.armor_asg       = 12
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=495, damage_type="slash" },
    { type="bite", as=486, damage_type="puncture" },
    { type="pound", as=478, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "troll_regeneration",
    "rend",
    "crushing_blow",
    "disease_touch",
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
Creature.skin            = "a tomb troll claw"
Creature.special_loot    = {
    "a troll-carved bone fetish",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11728,
    11729,
    11730,
    11731,
    11732,
    11733,
    11734,
    11735,
    11736,
    11737,
    11738,
    11739,
    11740,
    11741,
    11742,
    11743,
    11744,
    11745,
    11746,
    16179,
    16181,
    16209,
    16210,
    16213,
    17692
    }
Creature.roam_rooms      = {
    11728,
    11729,
    11730,
    11731,
    11732,
    11733,
    11734,
    11735,
    11736,
    11737,
    11738,
    11739,
    11740,
    11741,
    11742,
    11743,
    11744,
    11745,
    11746,
    16179,
    16181,
    16209,
    16210,
    16213,
    17692
    }
Creature.roam_chance     = 8
Creature.respawn_seconds = 720
Creature.max_count       = 3
Creature.description     = "The Tomb Troll has lived in the Marsh Keep long enough to have absorbed something of its character — which is to say, death and old stone and the specific damp of a building that has been slowly losing the battle against the marsh for centuries.  The skin has gone a deep, mottled grey, and the claws are long and black.  The regeneration that makes all trolls dangerous is in this specimen unusually rapid and visibly disturbing to observe."
return Creature
