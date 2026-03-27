-- Creature: giant fog beetle
-- Zone: Teras Isle / Greymist Wood  |  Level: 32
local Creature = {}
Creature.id              = 10203
Creature.name            = "giant fog beetle"
Creature.level           = 32
Creature.family          = "insect"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 400
Creature.hp_variance     = 33
Creature.ds_melee        = 258
Creature.ds_bolt         = 125
Creature.td_spiritual    = 104
Creature.td_elemental    = 104
Creature.udf             = 5
Creature.armor_asg       = 14
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=392, damage_type="puncture" },
    { type="claw", as=384, damage_type="slash" },
    { type="fog_spray", as=375, damage_type="unbalancing" },
}
Creature.spells          = {}
Creature.abilities       = {
    "armoured_shell",
    "fog_spray",
    "burrowing_escape",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a beetle carapace plate"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    1998,
    1999,
    2000,
    2001,
    2002,
    2003,
    2004,
    2005,
    2006,
    2007,
    2008,
    2009,
    2010,
    2021,
    2022,
    2023,
    2041,
    2042,
    2043,
    2044,
    2045,
    2046,
    2047,
    2048,
    2049,
    2050,
    2051,
    2052,
    12569,
    12570,
    2030,
    2031,
    2032,
    2033
    }
Creature.roam_rooms      = {
    1998,
    1999,
    2000,
    2001,
    2002,
    2003,
    2004,
    2005,
    2006,
    2007,
    2008,
    2009,
    2010,
    2021,
    2022,
    2023,
    2041,
    2042,
    2043,
    2044,
    2045,
    2046,
    2047,
    2048,
    2049,
    2050,
    2051,
    2052,
    12569,
    12570,
    2030,
    2031,
    2032,
    2033
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 540
Creature.max_count       = 4
Creature.description     = "The giant fog beetle of Teras Isle has evolved a specialised spray organ that releases a blinding chemical fog when threatened — a useful adaptation in a forest where visibility is already limited.  The carapace is a deep teal-green that functions as camouflage against the volcanic rock and dense vegetation, and the mandibles can shear through wood."
return Creature
