-- Creature: brown gak
-- Zone: Yander's Farm / Open Path & Barnyard  |  Level: 2
local Creature = {}

Creature.id              = 9104
Creature.name            = "brown gak"
Creature.level           = 2
Creature.family          = "gak"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 42
Creature.hp_variance     = 5

Creature.ds_melee        = 28
Creature.ds_bolt         = 12
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 2
Creature.armor_natural   = false

Creature.attacks = {
    { type="claw", as=38, damage_type="slash" },
    { type="bite", as=34, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a brown gak hide"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    6012,
    6013,
    6014,
    6016,
    6018,
    6019,
    6020,
    6021,
    6022,
    6023,
    6025,
    6026
}
Creature.roam_rooms = {
    6012,
    6013,
    6014,
    6015,
    6016,
    6017,
    6018,
    6019,
    6020,
    6021,
    6022,
    6023,
    6024,
    6025,
    6026,
    6027,
    6028,
    6029,
    6030
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 160
Creature.max_count       = 2

Creature.description = "Squat, roughly man-shaped, and covered in coarse brown fur, the brown gak shuffles about on stubby legs with its knuckles occasionally brushing the ground.  Beady black eyes glitter beneath a heavy brow, and a wide lipless mouth shows rows of flat crushing teeth.  It smells powerfully of wet fur and rotting vegetation."

return Creature
