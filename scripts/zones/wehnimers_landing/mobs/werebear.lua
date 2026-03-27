-- Creature: werebear
-- Zone: Upper Trollfang / Secluded Valley  |  Level: 10
local Creature = {}
Creature.id              = 9406
Creature.name            = "werebear"
Creature.level           = 10
Creature.family          = "werebear"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 138
Creature.hp_variance     = 10
Creature.ds_melee        = 112
Creature.ds_bolt         = 50
Creature.td_spiritual    = 36
Creature.td_elemental    = 36
Creature.udf             = 15
Creature.armor_asg       = 7
Creature.armor_natural   = true
Creature.attacks = {
    { type="claw", as=134, damage_type="slash" },
    { type="bite", as=128, damage_type="puncture" },
    { type="bear_hug", as=122, damage_type="crush" },
}
Creature.spells = {}
Creature.abilities = {
    "lycanthrope_regeneration",
    "curse_touch",
    "fear_aura",
}
Creature.immune    = {
    "disease",
    "poison",
}
Creature.resist    = {
    "pierce",
    "slash",
}
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = "a werebear claw"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    7319,
    7320,
    7321,
    7322,
    7323,
    7324
    }
Creature.roam_rooms = {
    7319,
    7320,
    7321,
    7322,
    7323,
    7324,
    7780,
    7781,
    7782
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 480
Creature.max_count       = 1
Creature.description = "In the dimness of the secluded valley, the werebear is a hunched, massive silhouette that could almost be mistaken for a large bear — until it rises to a bipedal stance and the intelligence in those amber eyes becomes apparent.  The cursed nature of the creature is visible in the way its form wavers between human and ursine, never fully settled into either state."
return Creature
