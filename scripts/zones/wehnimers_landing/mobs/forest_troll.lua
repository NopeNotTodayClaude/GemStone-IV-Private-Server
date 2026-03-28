-- Creature: forest troll
-- Zone: Upper Trollfang / Lower Trollfang  |  Level: 14
local Creature = {}
Creature.id              = 9410
Creature.name            = "forest troll"
Creature.level           = 14
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 180
Creature.hp_variance     = 14
Creature.ds_melee        = 133
Creature.ds_bolt         = 63
Creature.td_spiritual    = 46
Creature.td_elemental    = 46
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false
Creature.attacks = {
    { type="claw", as=177, damage_type="slash" },
    { type="bite", as=170, damage_type="puncture" },
    { type="pound", as=165, damage_type="crush" },
}
Creature.spells = {}
Creature.abilities = {
    "troll_regeneration",
    "rend",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a troll hide"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    4106,
    4107,
    4108,
    4109,
    4110,
    4111,
    4112,
    4113,
    4114,
    4115,
    4116,
    4117,
    7155,
    7156,
    7157
    }
Creature.roam_rooms = {
    4106,
    4107,
    4108,
    4109,
    4110,
    4111,
    4112,
    4113,
    4114,
    4115,
    4116,
    4117,
    7155,
    7156,
    7157,
    1290,
    1291,
    1292
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 360
Creature.max_count       = 2
Creature.description = "Bark-rough skin mottled in shades of grey-green and brown makes the forest troll surprisingly difficult to spot until it moves.  Massive limbs capable of tearing a tree from the ground hang nearly to the knees, and the face is a flattened, heavy-browed mask of perpetual aggression.  It regenerates wounds with unsettling speed — the only reliable solution is fire or magic."
return Creature
