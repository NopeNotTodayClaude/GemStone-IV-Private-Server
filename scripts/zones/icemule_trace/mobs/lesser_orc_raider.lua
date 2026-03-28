-- Creature: lesser orc raider
-- Zone: Icemule Trace / Glatoph foothills  |  Level: 9
local Creature = {}

Creature.id              = 10327
Creature.name            = "lesser orc raider"
Creature.level           = 9
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 128
Creature.hp_variance     = 10
Creature.ds_melee        = 86
Creature.ds_bolt         = 36
Creature.td_spiritual    = 24
Creature.td_elemental    = 24
Creature.udf             = 0
Creature.armor_asg       = 8
Creature.armor_natural   = false

Creature.attacks = {
    { type="handaxe", as=124, damage_type="slash" },
    { type="shortsword", as=118, damage_type="slash" },
}

Creature.spells = {}
Creature.abilities = { "battle_fury", "pack_tactics", "scavenge_weapon" }
Creature.immune    = {}
Creature.resist    = { "cold" }

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "an orc ear"
Creature.special_loot = { "a frost-stiffened raider token" }

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = { 2572, 2573, 2574, 2575, 2576, 2577, 2578 }
Creature.roam_rooms = { 2572, 2573, 2574, 2575, 2576, 2577, 2578, 2569, 2570, 2571 }

Creature.roam_chance     = 22
Creature.respawn_seconds = 320
Creature.max_count       = 1

Creature.description = "Wrapped in scavenged furs and half-frozen scraps of mail, the lesser orc raider moves with a hard northern swagger.  It carries the marks of repeated raids along the Glatoph approaches and keeps one eye fixed on anything that looks worth stealing."

return Creature
