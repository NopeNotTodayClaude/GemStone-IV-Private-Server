-- Creature: lava troll
-- Zone: Teras Isle / Volcanic Slope  |  Level: 34
local Creature = {}
Creature.id              = 10208
Creature.name            = "lava troll"
Creature.level           = 34
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 432
Creature.hp_variance     = 36
Creature.ds_melee        = 278
Creature.ds_bolt         = 135
Creature.td_spiritual    = 110
Creature.td_elemental    = 110
Creature.udf             = 0
Creature.armor_asg       = 11
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=422, damage_type="slash" },
    { type="bite", as=414, damage_type="puncture" },
    { type="lava_fist", as=406, damage_type="fire" },
}
Creature.spells          = {}
Creature.abilities       = {
    "troll_regeneration",
    "lava_skin",
    "fire_immunity",
    "rend",
}
Creature.immune          = {
    "fire",
}
Creature.resist          = {
    "cold",
}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a lava troll slag chunk"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    14694,
    14695,
    14696,
    14699,
    14704,
    14705,
    14719,
    14722,
    14723,
    14727,
    18076,
    12579,
    12580,
    12581
    }
Creature.roam_rooms      = {
    14694,
    14695,
    14696,
    14699,
    14704,
    14705,
    14719,
    14722,
    14723,
    14727,
    18076,
    12579,
    12580,
    12581
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 540
Creature.max_count       = 2
Creature.description     = "Evolved in the lava fields of Teras Isle, the lava troll's skin has incorporated volcanic minerals into its composition — which is to say, large parts of it are technically partially molten.  The regeneration common to all trolls is here enhanced by the ambient volcanic energy, and wounds close with a crust of cooling stone rather than mere flesh.  The fists leave scorch marks."
return Creature
