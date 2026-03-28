-- Creature: Neartofar troll champion
-- Zone: Neartofar Forest  |  Level: 18
local Creature = {}

Creature.id              = 6004
Creature.name            = "Neartofar troll champion"
Creature.level           = 18
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 245
Creature.hp_variance     = 18
Creature.ds_melee        = 146
Creature.ds_bolt         = 20
Creature.td_spiritual    = 60
Creature.td_elemental    = 60
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false

Creature.attacks = {
    { type = "longsword", as = 198, damage_type = "slash" },
    { type = "shield_bash", as = 188, damage_type = "crush" },
}

Creature.spells = {}
Creature.abilities = { "spirit_warding_2", "troll_regeneration", "shield_bash", "battle_rage" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a greasy troll scalp"
Creature.special_loot = { "a troll champion's torque" }

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = { 10643, 10644, 10650, 10651, 10652, 10653, 10654, 10655, 10656, 10657 }
Creature.roam_rooms = { 10643, 10644, 10650, 10651, 10652, 10653, 10654, 10655, 10656, 10657, 10658, 10659 }

Creature.roam_chance     = 16
Creature.respawn_seconds = 420
Creature.max_count       = 1

Creature.description = "Scarred even by troll standards, the Neartofar troll champion wears a bent iron gorget and carries itself like something used to winning ugly fights.  Thick cords of muscle shift under scarred skin, and the wounds that should have laid it low long ago have healed into a brutal map of old victories."

return Creature
