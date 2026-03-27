-- Creature: kobold
-- Zone: Vornavis / Coastal Cliffs  |  Level: 1
local Creature = {}
Creature.id              = 10101
Creature.name            = "kobold"
Creature.level           = 1
Creature.family          = "kobold"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 24
Creature.hp_variance     = 3
Creature.ds_melee        = 22
Creature.ds_bolt         = 8
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 2
Creature.armor_natural   = false
Creature.attacks         = {
    { type="dagger", as=22, damage_type="puncture" },
    { type="handaxe", as=18, damage_type="slash" },
}
Creature.spells          = {}
Creature.abilities       = {}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = false
Creature.loot_boxes      = true
Creature.skin            = "a tattered kobold skin"
Creature.special_loot    = {
    "a kobold ear",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    478,
    479,
    480,
    481,
    482,
    483,
    484,
    485,
    486,
    487,
    488,
    489,
    490,
    491,
    492,
    493
    }
Creature.roam_rooms      = {
    478,
    479,
    480,
    481,
    482,
    483,
    484,
    485,
    486,
    487,
    488,
    489,
    490,
    491,
    492,
    493
    }
Creature.roam_chance     = 35
Creature.respawn_seconds = 150
Creature.max_count       = 2
Creature.description     = "Scaly, yellow-eyed, and roughly the size of a large dog standing upright, the kobold lurks along the coastal cliffs looking for things to steal, ambush, or simply harass.  It smells powerfully of fish and low tide, and the crude weapons it carries are a testament to its scavenging ability rather than any manufacturing skill."
return Creature
