-- Creature: raider orc marauder
-- Zone: Ta'Vaalor outskirts / Yander's Farm  |  Level: 12
local Creature = {}

Creature.id              = 9204
Creature.name            = "raider orc marauder"
Creature.level           = 12
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 158
Creature.hp_variance     = 12
Creature.ds_melee        = 106
Creature.ds_bolt         = 50
Creature.td_spiritual    = 36
Creature.td_elemental    = 36
Creature.udf             = 0
Creature.armor_asg       = 9
Creature.armor_natural   = false

Creature.attacks = {
    { type="broadsword", as=154, damage_type="slash" },
    { type="handaxe", as=148, damage_type="slash" },
}

Creature.spells = {}
Creature.abilities = { "battle_rage", "pack_tactics", "scavenge_weapon" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "an orc ear"
Creature.special_loot = { "a marauder raid-mark" }

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    6073, 6074, 6075, 6076, 6077, 6078, 6079, 6080, 6081, 6082,
    6083, 6084, 6085, 6086, 6087, 6088, 6089, 6060, 6061, 6062,
    6063, 6064, 6065, 6066, 6067, 6068, 6069, 6070, 6071, 6072, 10261
}
Creature.roam_rooms = {
    6073, 6074, 6075, 6076, 6077, 6078, 6079, 6080, 6081, 6082,
    6083, 6084, 6085, 6086, 6087, 6088, 6089, 6060, 6061, 6062,
    6063, 6064, 6065, 6066, 6067, 6068, 6069, 6070, 6071, 6072,
    10261, 6024, 6041, 6042, 6043, 6044
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 340
Creature.max_count       = 1

Creature.description = "A veteran of repeated strikes into Vaalorian farmland, the raider orc marauder wears a mishmash of looted harness plates over scar-seamed hide and fights with ugly confidence.  Tokens of earlier raids hang from its belt in deliberate view, meant to impress its own kind and terrify anything softer."

return Creature
