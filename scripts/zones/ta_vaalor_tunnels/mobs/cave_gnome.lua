-- Creature: cave gnome
-- Zone: Ta'Vaalor Tunnels — Catacombs deep section  |  Level: 2
-- DB creature_id: 9304
--
-- SPAWN ZONE: Zul Logoth tunnels ONLY.
-- Rooms 5900-5940 are reserved for fanged_rodent exclusively.
-- Do NOT add rooms 5900-5940 here under any circumstance.
local Creature = {}
Creature.id              = 9304
Creature.name            = "cave gnome"
Creature.level           = 2
Creature.family          = "gnome"
Creature.classification  = "living"
Creature.body_type       = "humanoid"
Creature.hp_base         = 42
Creature.hp_variance     = 6
Creature.ds_melee        = 26
Creature.ds_bolt         = 14
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 5
Creature.armor_natural   = false
Creature.attacks = {
    { type="dagger",      as=38, damage_type="puncture" },
    { type="closed_fist", as=28, damage_type="crush"    },
}
Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins   = true
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a gnome scalp"
Creature.special_loot = {}
Creature.decay_seconds = 240
Creature.crumbles      = false
Creature.decay_message = ""
-- Spawn rooms: Zul Logoth tunnel sections only.
-- Add verified Zul Logoth room IDs here when that zone is built out.
-- Rooms 5900-5940 are FORBIDDEN — those belong to fanged_rodent.
Creature.spawn_rooms = {}
Creature.roam_rooms  = {}
Creature.roam_chance     = 15
Creature.respawn_seconds = 280
Creature.max_count       = 0
Creature.description     = "Pallid and nearly sightless from generations of cave-dwelling, the cave gnome has adapted fully to life underground.  Its eyes are milky and wide, its skin the colour of old chalk, and it moves through the dark with a confidence that borders on arrogance."
return Creature
