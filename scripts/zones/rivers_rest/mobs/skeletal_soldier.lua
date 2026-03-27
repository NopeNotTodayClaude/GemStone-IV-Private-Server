-- Creature: skeletal soldier
-- Zone: Miasmal Forest  |  Level: 34
local Creature = {}
Creature.id              = 10006
Creature.name            = "skeletal soldier"
Creature.level           = 34
Creature.family          = "skeleton"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 436
Creature.hp_variance     = 36
Creature.ds_melee        = 282
Creature.ds_bolt         = 138
Creature.td_spiritual    = 112
Creature.td_elemental    = 112
Creature.udf             = 295
Creature.armor_asg       = 8
Creature.armor_natural   = false
Creature.attacks         = {
    { type="longsword", as=340, damage_type="slash" },
    { type="shield_bash", as=332, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "undead_resilience",
    "formation_fighting",
}
Creature.immune          = {
    "disease",
    "poison",
}
Creature.resist          = {
    "pierce",
    "slash",
}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a bone shard"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11627,
    11628,
    11629,
    11630,
    11631,
    11632,
    11633,
    11634,
    11635,
    11636,
    11637,
    11638,
    11639,
    11640,
    11641,
    11642,
    11643,
    11644,
    11645,
    11650,
    11646,
    11664,
    11665,
    11666,
    11670,
    11675,
    11676
    }
Creature.roam_rooms      = {
    11627,
    11628,
    11629,
    11630,
    11631,
    11632,
    11633,
    11634,
    11635,
    11636,
    11637,
    11638,
    11639,
    11640,
    11641,
    11642,
    11643,
    11644,
    11645,
    11650,
    11646,
    11664,
    11665,
    11666,
    11670,
    11675,
    11676
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 480
Creature.max_count       = 4
Creature.description     = "Still wearing the rusted remains of military gear, the skeletal soldier moves with the muscle-memory of a lifetime of drill — stance correct, shield arm up, weapon extended.  The empty orbital sockets of its skull track movement with unnerving precision, and the jaw works silently as though still receiving orders.  Whatever army it served has been dust for centuries."
return Creature
