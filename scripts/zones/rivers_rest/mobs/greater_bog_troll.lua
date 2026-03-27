-- Creature: greater bog troll
-- Zone: Oteska's Haven  |  Level: 39
local Creature = {}
Creature.id              = 10010
Creature.name            = "greater bog troll"
Creature.level           = 39
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 492
Creature.hp_variance     = 41
Creature.ds_melee        = 312
Creature.ds_bolt         = 158
Creature.td_spiritual    = 126
Creature.td_elemental    = 126
Creature.udf             = 0
Creature.armor_asg       = 11
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=378, damage_type="slash" },
    { type="bite", as=370, damage_type="puncture" },
    { type="pound", as=362, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "troll_regeneration",
    "disease_touch",
    "bog_mire",
    "rend",
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
    11667,
    11668,
    11669,
    11671,
    11672,
    11673,
    11674,
    11677,
    11678,
    16147,
    11683,
    11684,
    11685,
    11686
    }
Creature.roam_rooms      = {
    11667,
    11668,
    11669,
    11671,
    11672,
    11673,
    11674,
    11677,
    11678,
    16147,
    11683,
    11684,
    11685,
    11686
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 540
Creature.max_count       = 2
Creature.description     = "Larger and more aggressive than the common bog troll, the greater bog troll has spent enough time in the deepest reaches of the miasmal waters to take on some of their quality.  The skin has the blackish tint of waterlogged wood, and the teeth have grown irregular and outward-pointing.  When it rises from the water it is slow — until suddenly it isn't."
return Creature
