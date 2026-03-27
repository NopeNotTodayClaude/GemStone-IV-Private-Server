-- Creature: bog wraith
-- Zone: Miasmal Forest  |  Level: 41
local Creature = {}
Creature.id              = 10008
Creature.name            = "bog wraith"
Creature.level           = 41
Creature.family          = "wraith"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 505
Creature.hp_variance     = 42
Creature.ds_melee        = 325
Creature.ds_bolt         = 165
Creature.td_spiritual    = 135
Creature.td_elemental    = 92
Creature.udf             = 342
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="wraith_touch", as=395, damage_type="unbalancing" },
    { type="life_drain", as=388, damage_type="cold" },
}
Creature.spells          = {
    { name="wraith_wail", cs=208, as=0 },
    { name="shadow_dispel", cs=202, as=0 },
}
Creature.abilities       = {
    "spirit_strike",
    "life_drain",
    "phase_through_terrain",
    "fear_aura",
    "soul_rend",
}
Creature.immune          = {
    "disease",
    "poison",
    "cold",
    "electricity",
}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = ""
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = true
Creature.decay_message   = "tears apart into tendrils of fog."
Creature.spawn_rooms     = {
    11651,
    11652,
    11653,
    11654,
    11655,
    11656,
    11657,
    16122,
    16124,
    16127,
    22218,
    22219,
    11647,
    11648,
    11649,
    11658,
    11659,
    11660,
    11661,
    11662,
    11663
    }
Creature.roam_rooms      = {
    11651,
    11652,
    11653,
    11654,
    11655,
    11656,
    11657,
    16122,
    16124,
    16127,
    22218,
    22219,
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
Creature.roam_chance     = 18
Creature.respawn_seconds = 600
Creature.max_count       = 2
Creature.description     = "The bog wraith moves through the miasmal forest as though it and the place were made of the same substance — which, in a meaningful sense, they are.  Its form is the mist given will: a billowing, vaguely human-shaped concentration of grey-green vapour through which eyes occasionally appear, burning with cold hatred.  The temperature drops sharply in its immediate vicinity, and the air smells of stagnant water and something older."
return Creature
