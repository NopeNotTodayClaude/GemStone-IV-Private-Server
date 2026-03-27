-- Creature: great boar
-- Zone: Yander's Farm / Wheat Fields  |  Level: 10
local Creature = {}
Creature.id              = 9201
Creature.name            = "great boar"
Creature.level           = 10
Creature.family          = "boar"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 132
Creature.hp_variance     = 10
Creature.ds_melee        = 94
Creature.ds_bolt         = 38
Creature.td_spiritual    = 30
Creature.td_elemental    = 30
Creature.udf             = 5
Creature.armor_asg       = 5
Creature.armor_natural   = true
Creature.attacks = {
    { type="gore", as=134, damage_type="puncture" },
    { type="charge", as=128, damage_type="crush" },
    { type="bite", as=122, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {
    "charge_knockdown",
    "tough_hide",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a boar tusk"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    6073,
    6074,
    6075,
    6076,
    6077,
    6078,
    6079,
    6080,
    6081,
    6082,
    6083,
    6084,
    6085,
    6086,
    6087,
    6088,
    6089
    }
Creature.roam_rooms = {
    6073,
    6074,
    6075,
    6076,
    6077,
    6078,
    6079,
    6080,
    6081,
    6082,
    6083,
    6084,
    6085,
    6086,
    6087,
    6088,
    6089,
    6060,
    6061,
    6062
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 2
Creature.description = "Massive and bristle-backed, the great boar stands nearly chest-high and weighs more than most warhorses.  Paired tusks curve outward and upward from a broad, flat snout, and small piggy eyes smolder with irritable hostility.  When it charges, the ground shakes underfoot and there is very little time to step aside."
return Creature
