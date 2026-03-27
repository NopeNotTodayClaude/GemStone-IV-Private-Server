-- Creature: siren lizard
-- Zone: Teras Isle / Eye of V'Tull  |  Level: 42
local Creature = {}
Creature.id              = 10210
Creature.name            = "siren lizard"
Creature.level           = 42
Creature.family          = "lizard"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 518
Creature.hp_variance     = 43
Creature.ds_melee        = 332
Creature.ds_bolt         = 168
Creature.td_spiritual    = 136
Creature.td_elemental    = 136
Creature.udf             = 8
Creature.armor_asg       = 11
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=508, damage_type="puncture" },
    { type="claw", as=500, damage_type="slash" },
    { type="mesmerizing_gaze", as=492, damage_type="unbalancing" },
}
Creature.spells          = {
    { name="sonic_lure", cs=212, as=0 },
}
Creature.abilities       = {
    "mesmerizing_gaze",
    "sonic_lure",
    "fire_immunity",
    "fast_reflexes",
}
Creature.immune          = {
    "fire",
}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a siren lizard scale"
Creature.special_loot    = {
    "a siren lizard vocal membrane",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    2122,
    2123,
    2124,
    2125,
    2126,
    2127,
    2128,
    2129,
    2130,
    2131,
    2132,
    2133,
    2134,
    2135,
    2136,
    2137,
    2138,
    2139,
    2140,
    2141
    }
Creature.roam_rooms      = {
    2122,
    2123,
    2124,
    2125,
    2126,
    2127,
    2128,
    2129,
    2130,
    2131,
    2132,
    2133,
    2134,
    2135,
    2136,
    2137,
    2138,
    2139,
    2140,
    2141
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 600
Creature.max_count       = 3
Creature.description     = "The siren lizard owes its name to the subsonic vibration it produces — a sound below hearing that nevertheless registers in the nervous system as an instruction to stop moving and look at the source.  By the time the cognitive brain overrides this instruction, the lizard is at close range.  The scales are iridescent red-orange against the lava flows, and the eyes are a yellow that seems to generate its own light."
return Creature
