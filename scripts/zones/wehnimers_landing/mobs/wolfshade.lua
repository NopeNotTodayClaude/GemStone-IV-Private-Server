-- Creature: wolfshade
-- Zone: Upper Trollfang / Twisted Trail  |  Level: 15
local Creature = {}
Creature.id              = 9413
Creature.name            = "wolfshade"
Creature.level           = 15
Creature.family          = "shade"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "quadruped"
Creature.hp_base         = 177
Creature.hp_variance     = 13
Creature.ds_melee        = 158
Creature.ds_bolt         = 75
Creature.td_spiritual    = 52
Creature.td_elemental    = 35
Creature.udf             = 185
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks = {
    { type="shadow_bite", as=178, damage_type="puncture" },
    { type="shadow_claw", as=172, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "spirit_strike",
    "shadow_meld",
    "fear_howl",
    "pack_tactics",
}
Creature.immune    = {
    "disease",
    "poison",
    "cold",
}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = ""
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = "dissolves into shadow with a faint howl."
Creature.spawn_rooms = {
    7780,
    7781,
    7782,
    7783,
    7784,
    7785,
    7786,
    7787,
    7788,
    6821,
    6822,
    6823,
    6824
    }
Creature.roam_rooms = {
    7780,
    7781,
    7782,
    7783,
    7784,
    7785,
    7786,
    7787,
    7788,
    6821,
    6822,
    6823,
    6824
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 400
Creature.max_count       = 1
Creature.description = "The wolfshade has the outline of a large wolf rendered entirely in shadow — no colour, no texture, just the negative space where a wolf should be.  It moves in total silence on paws that leave no prints, and its howl, when it comes, has a quality that seems to chill from the inside out.  The eyes are the only feature with any presence: two faint violet points of cold light."
return Creature
