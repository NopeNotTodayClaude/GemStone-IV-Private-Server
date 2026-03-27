-- Creature: relnak
-- Zone: Ta'Vaalor Tunnels — lower catacomb sections  |  Level: 3
-- DB creature_id: 9305
--
-- SPAWN ZONE: Lower catacomb rooms only (to be populated when confirmed).
-- Rooms 5900-5940 are reserved for fanged_rodent exclusively.
-- Do NOT add rooms 5900-5940 here under any circumstance.
local Creature = {}
Creature.id              = 9305
Creature.name            = "relnak"
Creature.level           = 3
Creature.family          = "reptile"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 52
Creature.hp_variance     = 8
Creature.ds_melee        = 34
Creature.ds_bolt         = 16
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 0
Creature.armor_asg       = 3
Creature.armor_natural   = true
Creature.attacks = {
    { type="stomp",  as=54, damage_type="crush"    },
    { type="bite",   as=46, damage_type="puncture" },
    { type="charge", as=42, damage_type="crush"    },
}
Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a relnak hide"
Creature.special_loot = {}
Creature.decay_seconds = 240
Creature.crumbles      = false
Creature.decay_message = ""
-- Spawn rooms: lower catacomb rooms only.
-- Add verified catacomb room IDs here when confirmed.
-- Rooms 5900-5940 are FORBIDDEN — those belong to fanged_rodent.
Creature.spawn_rooms = {}
Creature.roam_rooms  = {}
Creature.roam_chance     = 15
Creature.respawn_seconds = 300
Creature.max_count       = 0
Creature.description     = "The relnak is an ungainly bipedal creature about the height of a child.  Built like a collapsed arch with stubby forelimbs and a heavy tail, it compensates for its odd proportions with surprising aggression, charging anything that startles it with a shoulder-first impact that hits harder than it has any right to."
return Creature
