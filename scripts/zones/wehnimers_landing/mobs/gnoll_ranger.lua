-- Creature: gnoll ranger
-- Zone: Upper Trollfang / Imaera's Path  |  Level: 15
local Creature = {}
Creature.id              = 9412
Creature.name            = "gnoll ranger"
Creature.level           = 15
Creature.family          = "gnoll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 190
Creature.hp_variance     = 14
Creature.ds_melee        = 140
Creature.ds_bolt         = 68
Creature.td_spiritual    = 49
Creature.td_elemental    = 49
Creature.udf             = 5
Creature.armor_asg       = 7
Creature.armor_natural   = false
Creature.attacks = {
    { type="longbow", as=182, damage_type="puncture" },
    { type="shortsword", as=176, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "aimed_shot",
    "hamstring",
    "trackless_step",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a gnoll hide"
Creature.special_loot = {
    "a gnoll-carved bone arrowhead",
}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    4197,
    4198,
    4199,
    4200,
    4201,
    4202,
    4203,
    4204,
    4205,
    4206,
    4207,
    4208,
    4209,
    1287,
    1288,
    1289,
    1290,
    1291,
    1292
    }
Creature.roam_rooms = {
    4197,
    4198,
    4199,
    4200,
    4201,
    4202,
    4203,
    4204,
    4205,
    4206,
    4207,
    4208,
    4209,
    1287,
    1288,
    1289,
    1290,
    1291,
    1292
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 340
Creature.max_count       = 2
Creature.description = "Moving through the mountain terrain with the ease of long familiarity, the gnoll ranger is one of the most dangerous of its kind.  A heavy composite bow rests across its back, and a quiver of carved-bone arrows rattles with each loping stride.  The spotted hyena features are alert and focused, tracking prey through the alpine scrub with practiced patience."
return Creature
