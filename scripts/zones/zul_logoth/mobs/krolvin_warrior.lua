-- Creature: Krolvin warrior
-- Zone: Zul Logoth / Western DragonSpine  |  Level: 19
local Creature = {}
Creature.id              = 10409
Creature.name            = "Krolvin warrior"
Creature.level           = 19
Creature.family          = "krolvin"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 235
Creature.hp_variance     = 19
Creature.ds_melee        = 165
Creature.ds_bolt         = 80
Creature.td_spiritual    = 60
Creature.td_elemental    = 60
Creature.udf             = 0
Creature.armor_asg       = 11
Creature.armor_natural   = false
Creature.attacks         = {
    { type="broadsword", as=228, damage_type="slash" },
    { type="handaxe", as=222, damage_type="slash" },
    { type="shield_bash", as=215, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "battle_fury",
    "shield_bash",
    "krolvin_resilience",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a Krolvin ear"
Creature.special_loot    = {
    "a Krolvin warrior token",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    1018,
    1019,
    1020,
    1021,
    1022,
    1023,
    1024,
    1025
    }
Creature.roam_rooms      = {
    1018,
    1019,
    1020,
    1021,
    1022,
    1023,
    1024,
    1025
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 380
Creature.max_count       = 1
Creature.description     = "The Krolvin warrior is a product of a culture that values martial ability above all other traits — broad-shouldered, scarred from training before being scarred from combat, carrying weapons maintained to a standard that belies the rest of its rough appearance.  The grey-blue skin is covered in tribal markings applied at various life stages, and the yellow eyes miss very little.  Even in defeat it fights with the conviction that losing is simply not an acceptable outcome."
return Creature
