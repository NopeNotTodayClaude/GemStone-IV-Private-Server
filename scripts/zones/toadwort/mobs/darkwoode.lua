-- Creature: Darkwoode
-- Zone: The Toadwort / Blackened Morass  |  Level: 13
local Creature = {}

Creature.id              = 7012
Creature.name            = "Darkwoode"
Creature.level           = 13
Creature.family          = "darkwoode"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 160
Creature.hp_variance     = 12

Creature.ds_melee        = 136
Creature.ds_bolt         = 62
Creature.td_spiritual    = 46
Creature.td_elemental    = 46
Creature.udf             = 130
Creature.armor_asg       = 8
Creature.armor_natural   = false

Creature.attacks = {
    { type="claw", as=165, damage_type="slash" },
    { type="bite", as=158, damage_type="puncture" },
}

Creature.spells = {}
Creature.abilities = {
    "disease_touch",
    "fear_aura",
}
Creature.immune    = {
    "disease",
    "poison",
}
Creature.resist    = {}

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a darkwoode talon"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    10531, 10532, 10533, 10534, 10535, 10536, 10537, 10538, 10539
}

Creature.roam_rooms = {
    10529, 10530,
    10531, 10532, 10533, 10534, 10535, 10536, 10537, 10538, 10539
}

Creature.roam_chance     = 15
Creature.respawn_seconds = 340
Creature.max_count       = 1

Creature.description = "Resembling a warped, animate stump wrapped in sodden bark and swamp rot, the Darkwoode drags itself through the black mire with hateful purpose.  Tangled roots serve as feet, and pale fungus blooms from its split joints like diseased flowers."

return Creature
