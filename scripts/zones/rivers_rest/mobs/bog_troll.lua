-- Creature: bog troll
-- Zone: Miasmal Forest  |  Level: 35
local Creature = {}
Creature.id              = 10005
Creature.name            = "bog troll"
Creature.level           = 35
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 448
Creature.hp_variance     = 37
Creature.ds_melee        = 290
Creature.ds_bolt         = 142
Creature.td_spiritual    = 112
Creature.td_elemental    = 112
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=345, damage_type="slash" },
    { type="bite", as=338, damage_type="puncture" },
    { type="pound", as=332, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "troll_regeneration",
    "disease_touch",
    "bog_mire",
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
Creature.skin            = "a troll scalp"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11611,
    11612,
    11613,
    11614,
    11615,
    11616,
    11617,
    11618,
    11619,
    11620,
    11621,
    11622,
    11623,
    11624,
    11625,
    11626,
    11627,
    11628,
    11629,
    11630,
    11646,
    11664,
    11665,
    11666,
    11670,
    11675,
    11676
    }
Creature.roam_rooms      = {
    11611,
    11612,
    11613,
    11614,
    11615,
    11616,
    11617,
    11618,
    11619,
    11620,
    11621,
    11622,
    11623,
    11624,
    11625,
    11626,
    11627,
    11628,
    11629,
    11630,
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
Creature.description     = "Submerged to the neck in the black water of the miasmal forest, the bog troll is easy to miss until it surges upright — which is when its full size becomes apparent.  Weed and muck cling to bark-rough, dark green skin, and the smell that precedes it is an assault in itself.  The regenerative capacity of its kind means that wounds that would stop a lesser creature merely slow it down."
return Creature
