-- Creature: hobgoblin acolyte  |  Zone: muddy_village / Muddy Village  |  Level: 7
-- Source: gswiki.play.net/Hobgoblin_acolyte
-- HP: 100 | AS: bolt spells 104 AS, whip melee | DS: 50 | bolt: 34 | TD: 21 | ASG: 5
local Creature = {}

Creature.id              = 10426
Creature.name            = "hobgoblin acolyte"
Creature.level           = 7
Creature.family          = "goblin"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 100
Creature.hp_variance     = 10

Creature.ds_melee        = 50
Creature.ds_bolt         = 34
Creature.td_spiritual    = 21
Creature.td_elemental    = 21
Creature.udf             = 80
Creature.armor_asg       = 5
Creature.armor_natural   = false

Creature.attacks = {

}

Creature.spells = {

}
Creature.abilities = {  }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a hobgoblin scalp"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    29059, 29060, 29061, 29062, 29063, 29064, 29065, 29066, 29067, 29068, 29069, 29070, 29071, 29072, 29073
}

Creature.roam_rooms = {
    29059, 29060, 29061, 29062, 29063, 29064, 29065, 29066, 29067, 29068, 29069, 29070, 29071, 29072, 29073
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 240
Creature.max_count       = 5

Creature.description = "The hobgoblin acolyte has traded physical size for something more practical: the ability to hurl arcs of electricity and water from a distance. It is smaller than a standard hobgoblin and correspondingly faster, and it uses that speed to maintain range. The leather whip it carries is a last resort, but it swings it with the ease of long practice whenever you close the distance."

return Creature
