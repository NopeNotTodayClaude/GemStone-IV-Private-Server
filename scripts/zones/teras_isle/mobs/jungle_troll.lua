-- Creature: jungle troll
-- Zone: Teras Isle / Greymist Wood  |  Level: 26
local Creature = {}
Creature.id              = 10201
Creature.name            = "jungle troll"
Creature.level           = 26
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 320
Creature.hp_variance     = 26
Creature.ds_melee        = 225
Creature.ds_bolt         = 108
Creature.td_spiritual    = 84
Creature.td_elemental    = 84
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=312, damage_type="slash" },
    { type="bite", as=304, damage_type="puncture" },
    { type="pound", as=296, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "troll_regeneration",
    "camouflage",
    "rend",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a troll scalp"
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
    2042
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
    2042
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 480
Creature.max_count       = 2
Creature.description     = "The jungle troll has adapted to the dense, humid vegetation of Greymist Wood with a camouflage that would embarrass a chameleon — the warty skin shifts through greens and browns as it moves between light and shadow.  It is slower to attack than its moorland kin but far more patient, content to wait motionless until the ideal moment."
return Creature
