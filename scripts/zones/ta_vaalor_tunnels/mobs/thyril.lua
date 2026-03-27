-- Creature: thyril
-- Zone: Ta'Vaalor Tunnels — upper catacombs  |  Level: 2
-- DB creature_id: 9302 (catacomb variant)
--
-- SPAWN ZONE: Upper catacomb rooms only (to be populated when catacomb
-- rooms are confirmed).
-- Rooms 5900-5940 are reserved for fanged_rodent exclusively.
-- Do NOT add rooms 5900-5940 here under any circumstance.
local Creature = {}
Creature.id              = 9302
Creature.name            = "thyril"
Creature.level           = 2
Creature.family          = "feline"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 44
Creature.hp_variance     = 6
Creature.ds_melee        = 32
Creature.ds_bolt         = 18
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 2
Creature.armor_natural   = true
Creature.attacks = {
    { type="claw", as=36, damage_type="slash"    },
    { type="bite", as=30, damage_type="puncture" },
}
Creature.spells    = {}
Creature.abilities = { "stealth_ambush" }
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a thyril pelt"
Creature.special_loot = {}
Creature.decay_seconds = 220
Creature.crumbles      = false
Creature.decay_message = ""
-- Spawn rooms: upper catacomb rooms only.
-- Add verified catacomb room IDs here when confirmed.
-- Rooms 5900-5940 are FORBIDDEN — those belong to fanged_rodent.
Creature.spawn_rooms = {}
Creature.roam_rooms  = {}
Creature.roam_chance     = 20
Creature.respawn_seconds = 260
Creature.max_count       = 0
Creature.description     = "A young thyril has claimed territory among the upper catacombs.  It moves with predatory patience, pausing at each shadow as though taking inventory of everything within reach."
return Creature
