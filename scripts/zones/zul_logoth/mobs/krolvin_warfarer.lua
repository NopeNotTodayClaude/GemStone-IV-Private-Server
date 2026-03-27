-- Creature: Krolvin warfarer
-- Zone: Zul Logoth / Western DragonSpine  |  Level: 25
local Creature = {}
Creature.id              = 10410
Creature.name            = "Krolvin warfarer"
Creature.level           = 25
Creature.family          = "krolvin"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 305
Creature.hp_variance     = 25
Creature.ds_melee        = 212
Creature.ds_bolt         = 102
Creature.td_spiritual    = 80
Creature.td_elemental    = 80
Creature.udf             = 0
Creature.armor_asg       = 12
Creature.armor_natural   = false
Creature.attacks         = {
    { type="longsword", as=298, damage_type="slash" },
    { type="military_pick", as=290, damage_type="puncture" },
    { type="shield_bash", as=282, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "battle_fury",
    "shield_bash",
    "krolvin_resilience",
    "war_hardened",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a Krolvin ear"
Creature.special_loot    = {
    "a Krolvin warfarer badge",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    1022,
    1023,
    1024,
    1025,
    1026,
    1027,
    1028,
    1029,
    1030,
    1031
    }
Creature.roam_rooms      = {
    1022,
    1023,
    1024,
    1025,
    1026,
    1027,
    1028,
    1029,
    1030,
    1031
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 420
Creature.max_count       = 1
Creature.description     = "Where the warrior is a product of training, the Krolvin warfarer is a product of experience — and the experience has not been gentle.  The face carries the specific weathering of someone who has fought in multiple campaigns, and the way it reads terrain and opponent simultaneously speaks to hard-won tactical awareness.  The equipment it carries is better quality than the warrior's, and it uses it with the economy of someone for whom every motion in a fight is deliberate."
return Creature
