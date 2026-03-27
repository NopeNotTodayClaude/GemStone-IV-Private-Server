-- Creature: greater fetid corpse
-- Zone: Oteska's Haven  |  Level: 42
local Creature = {}
Creature.id              = 10013
Creature.name            = "greater fetid corpse"
Creature.level           = 42
Creature.family          = "zombie"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 518
Creature.hp_variance     = 43
Creature.ds_melee        = 335
Creature.ds_bolt         = 168
Creature.td_spiritual    = 136
Creature.td_elemental    = 136
Creature.udf             = 345
Creature.armor_asg       = 7
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=408, damage_type="slash" },
    { type="bite", as=400, damage_type="puncture" },
    { type="pound", as=392, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "disease_touch",
    "infectious_bite",
    "fetid_cloud",
    "shambling_charge",
}
Creature.immune          = {
    "disease",
    "poison",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a fetid corpse finger"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11667,
    11668,
    11669,
    11671,
    11672,
    11673,
    11674,
    11677,
    11678,
    16147,
    11647,
    11648,
    11649,
    11658,
    11659,
    11660,
    11661,
    11662,
    11663
    }
Creature.roam_rooms      = {
    11667,
    11668,
    11669,
    11671,
    11672,
    11673,
    11674,
    11677,
    11678,
    16147,
    11647,
    11648,
    11649,
    11658,
    11659,
    11660,
    11661,
    11662,
    11663
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 600
Creature.max_count       = 2
Creature.description     = "The greater fetid corpse is something the swamp has been working on for a long time — a body so thoroughly saturated with the marsh's energies that the boundary between corpse and swamp ecosystem has become blurred.  Swamp growth covers it like armour; insects and small creatures live in the cavities of its body.  The smell that accompanies it is a genuine physical assault, and the disease it carries is correspondingly virulent."
return Creature
