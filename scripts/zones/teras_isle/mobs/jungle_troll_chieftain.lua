-- Creature: jungle troll chieftain
-- Zone: Teras Isle / Greymist Wood  |  Level: 30
local Creature = {}
Creature.id              = 10202
Creature.name            = "jungle troll chieftain"
Creature.level           = 30
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 368
Creature.hp_variance     = 30
Creature.ds_melee        = 255
Creature.ds_bolt         = 125
Creature.td_spiritual    = 96
Creature.td_elemental    = 96
Creature.udf             = 0
Creature.armor_asg       = 11
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=350, damage_type="slash" },
    { type="bite", as=342, damage_type="puncture" },
    { type="pound", as=334, damage_type="crush" },
}
Creature.spells          = {
    { name="battle_cry", cs=148, as=0 },
}
Creature.abilities       = {
    "troll_regeneration",
    "chieftain_war_cry",
    "rally_trolls",
    "rend",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a troll chieftain war-trophy"
Creature.special_loot    = {
    "a chieftain's carved bone idol",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
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
    2032
    }
Creature.roam_rooms      = {
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
    2032
    }
Creature.roam_chance     = 10
Creature.respawn_seconds = 600
Creature.max_count       = 1
Creature.description     = "The chieftain of the greymist wood trolls is distinguished by the elaborate war-markings gouged into its hide and the cluster of bones and feathers bound into its matted crest.  Broader across the shoulders than its subordinates, it leads through dominance as much as authority — the scars on its face indicate a lifetime of maintaining that position against challengers."
return Creature
