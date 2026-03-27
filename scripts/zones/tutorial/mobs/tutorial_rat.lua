-- Creature: giant rat (tutorial)
-- Zone: tutorial  |  Level: 1
-- Scripted tutorial encounter — not a wild spawn.
-- respawn_seconds = 9999 keeps it from respawning during a session.
local Creature = {}

Creature.id              = 9901
Creature.name            = "giant rat"
Creature.level           = 1
Creature.family          = "rodent"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 20
Creature.hp_variance     = 0

Creature.ds_melee        = 10
Creature.ds_bolt         = 5
Creature.td_spiritual    = 0
Creature.td_elemental    = 0
Creature.udf             = 5
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 30, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = true
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = nil
Creature.special_loot = {}

Creature.decay_seconds  = 120
Creature.crumbles       = false
Creature.decay_message  = ""

Creature.spawn_rooms = { 59051 }
Creature.roam_rooms  = { 59051 }

Creature.roam_chance     = 0
Creature.respawn_seconds = 9999
Creature.max_count       = 1

Creature.description = "A large, mangy rat with beady red eyes and yellowed fangs.  It hisses menacingly as it regards you."

return Creature
