-- Creature: rock troll zombie
-- Zone: Zul Logoth / Troll Burial Grounds  |  Level: 34
local Creature = {}
Creature.id              = 10405
Creature.name            = "rock troll zombie"
Creature.level           = 34
Creature.family          = "troll"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 435
Creature.hp_variance     = 36
Creature.ds_melee        = 280
Creature.ds_bolt         = 138
Creature.td_spiritual    = 112
Creature.td_elemental    = 112
Creature.udf             = 345
Creature.armor_asg       = 12
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=338, damage_type="slash" },
    { type="bite", as=330, damage_type="puncture" },
    { type="pound", as=322, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "undead_resilience",
    "disease_touch",
    "stone_skin",
}
Creature.immune          = {
    "disease",
    "poison",
}
Creature.resist          = {
    "slash",
    "pierce",
}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a zombie troll chunk"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    5808,
    5809,
    5810,
    5811,
    5812,
    5813,
    5814,
    5815,
    5816,
    5817,
    5818,
    5819,
    5820,
    5821,
    5822,
    5752,
    5753,
    5754,
    5756
    }
Creature.roam_rooms      = {
    5808,
    5809,
    5810,
    5811,
    5812,
    5813,
    5814,
    5815,
    5816,
    5817,
    5818,
    5819,
    5820,
    5821,
    5822,
    5752,
    5753,
    5754,
    5756
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 540
Creature.max_count       = 2
Creature.description     = "The rock troll's legendary physical durability extends somewhat into undeath — the stone-hard skin that protects the living troll continues to function in the zombie, providing armour against physical attacks that would end a softer animated corpse.  The regeneration is gone, replaced by the stubborn insistence of undeath, which amounts to the same thing from most adventurers' perspective."
return Creature
