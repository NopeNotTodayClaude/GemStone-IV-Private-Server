-- Creature: luminous spectre
-- Zone: Ghastly Swamp  |  Level: 35
local Creature = {}
Creature.id              = 10009
Creature.name            = "luminous spectre"
Creature.level           = 35
Creature.family          = "spectre"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 448
Creature.hp_variance     = 37
Creature.ds_melee        = 292
Creature.ds_bolt         = 148
Creature.td_spiritual    = 118
Creature.td_elemental    = 80
Creature.udf             = 298
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="spectral_touch", as=348, damage_type="unbalancing" },
    { type="cold_beam", as=342, damage_type="cold" },
}
Creature.spells          = {
    { name="spirit_slayer", cs=178, as=0 },
    { name="luminous_burst", cs=172, as=0 },
}
Creature.abilities       = {
    "spirit_strike",
    "blinding_flash",
    "phase_through_terrain",
    "fear_aura",
}
Creature.immune          = {
    "disease",
    "poison",
    "cold",
}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = ""
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = true
Creature.decay_message   = "flares brilliantly and goes dark."
Creature.spawn_rooms     = {
    11647,
    11648,
    11649,
    11658,
    11659,
    11660,
    11661,
    11662,
    11663,
    11646,
    11664,
    11665,
    11666,
    11670,
    11675,
    11676
    }
Creature.roam_rooms      = {
    11647,
    11648,
    11649,
    11658,
    11659,
    11660,
    11661,
    11662,
    11663,
    11646,
    11664,
    11665,
    11666,
    11670,
    11675,
    11676,
    16124,
    16127,
    22218,
    22219
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 540
Creature.max_count       = 2
Creature.description     = "Unlike most undead spirits, the luminous spectre is immediately visible — it radiates a cold, sickly blue-white light that illuminates the swamp in shifting patterns.  This visibility is deceptive.  The light draws the eye while the actual source of danger, the spirit's extremities, approach from unexpected angles.  The glow intensifies dramatically in the moment before it strikes, making the attack both telegraphed and somehow impossible to avoid."
return Creature
