-- Creature: fire salamander
-- Zone: Vornavis / North Beach  |  Level: 3
local Creature = {}
Creature.id              = 10106
Creature.name            = "fire salamander"
Creature.level           = 3
Creature.family          = "salamander"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 54
Creature.hp_variance     = 4
Creature.ds_melee        = 38
Creature.ds_bolt         = 18
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 3
Creature.armor_asg       = 3
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=56, damage_type="puncture" },
    { type="claw", as=52, damage_type="slash" },
    { type="fire_spit", as=48, damage_type="fire" },
}
Creature.spells          = {}
Creature.abilities       = {
    "fire_spit",
    "heat_aura",
}
Creature.immune          = {
    "fire",
}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a salamander skin"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    7603,
    7604,
    7605,
    7606,
    7607,
    7608,
    7613,
    7615
    }
Creature.roam_rooms      = {
    7603,
    7604,
    7605,
    7606,
    7607,
    7608,
    7613,
    7615
    }
Creature.roam_chance     = 25
Creature.respawn_seconds = 180
Creature.max_count       = 1
Creature.description     = "Jet black with vivid orange and yellow markings, the fire salamander of North Beach is a close cousin to those found in the catacombs of Wehnimer's Landing.  The beach variant is slightly smaller but no less dangerous, and has adapted to using the reflection of sunlight off the water as concealment."
return Creature
