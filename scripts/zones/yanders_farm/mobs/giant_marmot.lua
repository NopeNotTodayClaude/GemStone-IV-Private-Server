-- Creature: giant marmot
-- Zone: Yander's Farm / Wheat Fields  |  Level: 10
local Creature = {}
Creature.id              = 9202
Creature.name            = "giant marmot"
Creature.level           = 10
Creature.family          = "rodent"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 130
Creature.hp_variance     = 10
Creature.ds_melee        = 98
Creature.ds_bolt         = 40
Creature.td_spiritual    = 30
Creature.td_elemental    = 30
Creature.udf             = 3
Creature.armor_asg       = 3
Creature.armor_natural   = true
Creature.attacks = {
    { type="bite", as=128, damage_type="puncture" },
    { type="claw", as=122, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "burrowing_escape",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a marmot pelt"
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
    6089,
    6060,
    6061,
    6062,
    6063
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
    6062,
    6063
    }
Creature.roam_chance     = 25
Creature.respawn_seconds = 260
Creature.max_count       = 2
Creature.description = "This oversized cousin of the common groundhog comes up to knee height and weighs somewhere near two hundred pounds.  Covered in coarse brown-grey fur, the giant marmot stands up on its hind legs to survey the surrounding wheat field, whistle-squeaking in alarm before dropping to all fours and charging with surprising aggression."
return Creature
