-- Creature: firethorn shoot
-- Zone: Teras Isle / Eye of V'Tull  |  Level: 44
local Creature = {}
Creature.id              = 10211
Creature.name            = "firethorn shoot"
Creature.level           = 44
Creature.family          = "plant"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 540
Creature.hp_variance     = 45
Creature.ds_melee        = 348
Creature.ds_bolt         = 178
Creature.td_spiritual    = 148
Creature.td_elemental    = 148
Creature.udf             = 0
Creature.armor_asg       = 9
Creature.armor_natural   = true
Creature.attacks         = {
    { type="thorn_strike", as=530, damage_type="puncture" },
    { type="fire_thorn", as=522, damage_type="fire" },
    { type="entangle", as=514, damage_type="unbalancing" },
}
Creature.spells          = {}
Creature.abilities       = {
    "thorn_barrage",
    "fire_immunity",
    "entangle",
    "root_strike",
}
Creature.immune          = {
    "fire",
    "poison",
}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a firethorn cutting"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    2137,
    2138,
    2139,
    2140,
    2141,
    2142,
    2143,
    2144,
    2145,
    2146,
    2147,
    2148,
    2149,
    2150,
    2151,
    2152,
    2153,
    2176,
    2177,
    2178,
    2179,
    12763,
    2154,
    2155,
    2156,
    2157,
    2158
    }
Creature.roam_rooms      = {
    2137,
    2138,
    2139,
    2140,
    2141,
    2142,
    2143,
    2144,
    2145,
    2146,
    2147,
    2148,
    2149,
    2150,
    2151,
    2152,
    2153,
    2176,
    2177,
    2178,
    2179,
    12763,
    2154,
    2155,
    2156,
    2157,
    2158
    }
Creature.roam_chance     = 8
Creature.respawn_seconds = 600
Creature.max_count       = 4
Creature.description     = "An ambulatory thornbush that has incorporated the volcanic chemistry of Teras Isle into its biology, the firethorn shoot moves on a tangle of deep roots that serve as legs.  The thorns are superheated by internal chemistry and deliver burns as well as punctures.  The plant is not truly intelligent but responds to approach with immediate, mechanical aggression, and the speed of its reactions belies its vegetable nature."
return Creature
