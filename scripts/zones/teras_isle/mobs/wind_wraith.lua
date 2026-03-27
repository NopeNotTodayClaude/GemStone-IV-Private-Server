-- Creature: wind wraith
-- Zone: Teras Isle / Wind Tunnel  |  Level: 61
local Creature = {}
Creature.id              = 10212
Creature.name            = "wind wraith"
Creature.level           = 61
Creature.family          = "wraith"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 718
Creature.hp_variance     = 59
Creature.ds_melee        = 455
Creature.ds_bolt         = 232
Creature.td_spiritual    = 196
Creature.td_elemental    = 130
Creature.udf             = 475
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks         = {
    { type="wind_strike", as=702, damage_type="unbalancing" },
    { type="spectral_touch", as=692, damage_type="cold" },
    { type="gale_blast", as=680, damage_type="crush" },
}
Creature.spells          = {
    { name="cyclone", cs=310, as=0 },
    { name="wraith_wail", cs=305, as=0 },
    { name="wind_shear", cs=298, as=0 },
}
Creature.abilities       = {
    "spirit_strike",
    "cyclone",
    "gale_force",
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
Creature.decay_message   = "disperses into a rushing gust that howls away through the tunnel."
Creature.spawn_rooms     = {
    2167,
    2168,
    2169,
    2170,
    2171,
    2172,
    2173,
    2174,
    12764,
    12765,
    12766,
    12767
    }
Creature.roam_rooms      = {
    2167,
    2168,
    2169,
    2170,
    2171,
    2172,
    2173,
    2174,
    12764,
    12765,
    12766,
    12767
    }
Creature.roam_chance     = 10
Creature.respawn_seconds = 1200
Creature.max_count       = 1
Creature.description     = "The wind wraith is to air what the bog wraith is to water — a medium given will and malevolence.  It appears as a vortex of high-speed air with a humanoid shape intermittently visible at the center, maintained for just long enough to taunt before it collapses back into cyclonic ambiguity.  The tunnel that is its territory amplifies the force of its wind attacks to devastating effect."
return Creature
