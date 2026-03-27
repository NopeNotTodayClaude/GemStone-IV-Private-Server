-- Creature: specter
-- Zone: Vornavis / Mossy Caverns  |  Level: 14
local Creature = {}
Creature.id              = 10112
Creature.name            = "specter"
Creature.level           = 14
Creature.family          = "spectre"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 178
Creature.hp_variance     = 14
Creature.ds_melee        = 125
Creature.ds_bolt         = 60
Creature.td_spiritual    = 46
Creature.td_elemental    = 30
Creature.udf             = 148
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="spectral_touch", as=172, damage_type="unbalancing" },
    { type="chill_touch", as=165, damage_type="cold" },
}
Creature.spells          = {
    { name="spirit_slayer", cs=78, as=0 },
    { name="nightmare", cs=72, as=0 },
}
Creature.abilities       = {
    "spirit_strike",
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
Creature.decay_message   = "disperses into a cold mist."
Creature.spawn_rooms     = {
    7734,
    7735,
    7736,
    7737,
    7738,
    7739,
    7740,
    7741,
    7742,
    7743,
    7744,
    7745,
    7746,
    7747,
    7748,
    7749,
    7750,
    7751,
    7752,
    7753,
    7754,
    7755
    }
Creature.roam_rooms      = {
    7734,
    7735,
    7736,
    7737,
    7738,
    7739,
    7740,
    7741,
    7742,
    7743,
    7744,
    7745,
    7746,
    7747,
    7748,
    7749,
    7750,
    7751,
    7752,
    7753,
    7754,
    7755,
    7729,
    7730,
    7731,
    7732,
    7733
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 340
Creature.max_count       = 3
Creature.description     = "In the deepest and dampest of the mossy caverns, the specter drifts between formations of pale stone.  It is more visible here than its kind usually is, because the moisture in the air condenses around its form, giving it a semi-solid appearance that is somehow more unsettling than pure invisibility.  The cold it generates keeps the deep caverns below comfortable temperatures year-round."
return Creature
