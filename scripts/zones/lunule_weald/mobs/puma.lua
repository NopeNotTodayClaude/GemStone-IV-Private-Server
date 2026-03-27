-- Creature: puma
-- Zone: Lunule Weald / Knoll  |  Level: 15
local Creature = {}
Creature.id              = 9504
Creature.name            = "puma"
Creature.level           = 15
Creature.family          = "feline"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 188
Creature.hp_variance     = 14
Creature.ds_melee        = 142
Creature.ds_bolt         = 65
Creature.td_spiritual    = 49
Creature.td_elemental    = 49
Creature.udf             = 8
Creature.armor_asg       = 2
Creature.armor_natural   = true
Creature.attacks = {
    { type="claw", as=182, damage_type="slash" },
    { type="bite", as=176, damage_type="puncture" },
    { type="pounce", as=170, damage_type="crush" },
}
Creature.spells = {}
Creature.abilities = {
    "pounce_maneuver",
    "stealth_ambush",
    "hamstring",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a puma pelt"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    10545,
    10546,
    10552,
    10553,
    10554,
    10555,
    10547,
    10559,
    10560,
    10561
    }
Creature.roam_rooms = {
    10545,
    10546,
    10552,
    10553,
    10554,
    10555,
    10547,
    10559,
    10560,
    10561
    }
Creature.roam_chance     = 22
Creature.respawn_seconds = 320
Creature.max_count       = 1
Creature.description = "Tawny and compact, the puma of the Lunule Weald is both sleeker and more aggressive than those found in gentler terrain.  Long exposure to the corrupted air of the Weald has made the local population irritable beyond normal feline temperament, and they attack with a ferocity that seems personal.  The amber eyes track everything, and the reaction time borders on the supernatural."
return Creature
