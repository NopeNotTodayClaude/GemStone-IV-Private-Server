-- Creature: Urgh
-- Zone: Vornavis / West Road  |  Level: 4
local Creature = {}
Creature.id              = 10103
Creature.name            = "Urgh"
Creature.level           = 4
Creature.family          = "urgh"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 62
Creature.hp_variance     = 5
Creature.ds_melee        = 44
Creature.ds_bolt         = 22
Creature.td_spiritual    = 12
Creature.td_elemental    = 12
Creature.udf             = 0
Creature.armor_asg       = 4
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=64, damage_type="slash" },
    { type="bite", as=60, damage_type="puncture" },
}
Creature.spells          = {}
Creature.abilities       = {}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "an urgh hide"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    7601,
    7673,
    7674,
    7675,
    7676,
    7677,
    7678,
    7679,
    7680,
    7681,
    213,
    214,
    215,
    216,
    217,
    218
    }
Creature.roam_rooms      = {
    7601,
    7673,
    7674,
    7675,
    7676,
    7677,
    7678,
    7679,
    7680,
    7681,
    213,
    214,
    215,
    216,
    217,
    218
    }
Creature.roam_chance     = 30
Creature.respawn_seconds = 180
Creature.max_count       = 2
Creature.description     = "Squat and toad-like in general proportion, the Urgh has overlapping flaps of thick skin that serve admirably as natural armour and give it a permanently crumpled appearance.  The wide mouth holds more teeth than seem anatomically warranted, and the eyes, set flat on the sides of the head, provide a panoramic view of potential threats — and prey."
return Creature
