-- fanged rodent — Ta'Vaalor Tunnels zone
-- The authoritative fanged_rodent definition lives in:
--   scripts/zones/tavaalor/mobs/fanged_rodent.lua
-- This file intentionally has no spawn_rooms to avoid duplication.
local Creature = {}
Creature.id              = 7001
Creature.name            = "fanged rodent"
Creature.level           = 1
Creature.family          = "rodent"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 18
Creature.hp_variance     = 4
Creature.ds_melee        = 12
Creature.ds_bolt         = 8
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true
Creature.attacks = {
    { type = "bite", as = 22, damage_type = "puncture" },
    { type = "claw", as = 18, damage_type = "slash"    },
}
Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a fanged rodent pelt"
Creature.special_loot = {}
Creature.decay_seconds = 120
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {}
Creature.roam_rooms  = {}
Creature.roam_chance     = 40
Creature.respawn_seconds = 150
Creature.max_count       = 0
return Creature
