-- Creature: brown boar
-- Zone: Neartofar Forest | Forest & Riverside | Level: 13
local Creature = {}

Creature.id              = 6005
Creature.name            = "brown boar"
Creature.level           = 13
Creature.family          = "boar"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 166
Creature.hp_variance     = 12

Creature.ds_melee        = 116
Creature.ds_bolt         = 54
Creature.td_spiritual    = 42
Creature.td_elemental    = 42
Creature.udf             = 4
Creature.armor_asg       = 5
Creature.armor_natural   = true

Creature.attacks = {
    { type = "gore",   as = 164, damage_type = "puncture" },
    { type = "charge", as = 156, damage_type = "crush" },
    { type = "bite",   as = 150, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = { "charge_knockdown" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a brown boar skin"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    10622, 10623, 10624, 10625, 10626, 10627, 10628,
    10629, 10630, 10631, 10632,
    10633, 10634, 10635, 10636, 10637
}

Creature.roam_rooms = {
    10622, 10623, 10624, 10625, 10626, 10627, 10628,
    10629, 10630, 10631, 10632,
    10633, 10634, 10635, 10636, 10637,
    10638, 10639, 10640, 10641, 10642
}

Creature.roam_chance     = 18
Creature.respawn_seconds = 320
Creature.max_count       = 2

Creature.description = "Heavy-shouldered and mud-streaked, the brown boar roots through the leaf litter with a steady, ill-tempered persistence.  Its tusks are shorter than those of older specimens, but the bulk behind a charge is more than enough to break bone."

return Creature
