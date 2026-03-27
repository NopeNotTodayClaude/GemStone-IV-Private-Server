-- Creature: fire giant
-- Zone: Teras Isle / Volcanic Slope  |  Level: 36
local Creature = {}
Creature.id              = 10209
Creature.name            = "fire giant"
Creature.level           = 36
Creature.family          = "giant"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 455
Creature.hp_variance     = 37
Creature.ds_melee        = 292
Creature.ds_bolt         = 142
Creature.td_spiritual    = 115
Creature.td_elemental    = 115
Creature.udf             = 0
Creature.armor_asg       = 12
Creature.armor_natural   = false
Creature.attacks         = {
    { type="greatsword", as=445, damage_type="slash" },
    { type="fist", as=438, damage_type="crush" },
    { type="fire_hurl", as=430, damage_type="fire" },
}
Creature.spells          = {
    { name="fire_bolt", cs=180, as=0 },
    { name="immolate", cs=175, as=0 },
}
Creature.abilities       = {
    "fire_hurl",
    "call_fire",
    "stomp",
    "fire_immunity",
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
Creature.skin            = "a fire giant ember shard"
Creature.special_loot    = {
    "a fire giant flame-forged token",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    14719,
    14722,
    14723,
    14727,
    18076,
    2122,
    2123,
    2124,
    2125
    }
Creature.roam_rooms      = {
    14719,
    14722,
    14723,
    14727,
    18076,
    2122,
    2123,
    2124,
    2125
    }
Creature.roam_chance     = 8
Creature.respawn_seconds = 600
Creature.max_count       = 1
Creature.description     = "Clad in armour of black volcanic steel and standing a full fifteen feet, the fire giant is as much a feature of Teras Isle's landscape as the volcano itself.  The sword it carries was forged in a lava flow and cooled in the open air, a process that leaves the edge microscopically irregular in the way that makes certain volcanic blades prized by smiths.  The heat it radiates is extreme; proximity requires either magical protection or an extremely high pain tolerance."
return Creature
