-- Creature: coyote
-- Zone: Upper Trollfang  |  Level: 5
local Creature = {}
Creature.id              = 9402
Creature.name            = "coyote"
Creature.level           = 5
Creature.family          = "canine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 74
Creature.hp_variance     = 7
Creature.ds_melee        = 58
Creature.ds_bolt         = 28
Creature.td_spiritual    = 15
Creature.td_elemental    = 15
Creature.udf             = 4
Creature.armor_asg       = 1
Creature.armor_natural   = true
Creature.attacks = {
    { type="bite", as=76, damage_type="puncture" },
    { type="claw", as=70, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "pack_tactics",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a coyote tail"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    452,
    453,
    454,
    455,
    456,
    457,
    458,
    459,
    460,
    461,
    462,
    463,
    464,
    465,
    466,
    467,
    468,
    469,
    470,
    471,
    472,
    473,
    474,
    475,
    1196,
    1197,
    1198,
    1199,
    1200,
    1201
    }
Creature.roam_rooms = {
    452,
    453,
    454,
    455,
    456,
    457,
    458,
    459,
    460,
    461,
    462,
    463,
    464,
    465,
    466,
    467,
    468,
    469,
    470,
    471,
    472,
    473,
    474,
    475,
    1196,
    1197,
    1198,
    1199,
    1200,
    1201
    }
Creature.roam_chance     = 30
Creature.respawn_seconds = 220
Creature.max_count       = 4
Creature.description = "A lean, grizzled tawny canine that has carved out territory among the trollfang scrub.  It watches from a safe distance before committing to attack, preferring to circle with others of its kind to find the weakest point of approach.  The trollfang variety is measurably more aggressive than lowland coyotes, hardened by competition with larger predators."
return Creature
