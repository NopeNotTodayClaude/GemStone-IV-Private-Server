-- Creature: leaper
-- Zone: solhaven / Coastal Cliffs upper  |  Level: 6
-- Source: gswiki.play.net/Leaper
-- HP: 69 | AS: bite/claw/stomp 94 AS | DS: 19 | bolt DS: 9 | TD: 18
-- ASG: 5N | Body: quadruped
-- Treasure: no coins | Skin: a leaper hide
local Creature = {}
Creature.id              = 10419
Creature.name            = "leaper"
Creature.level           = 6
Creature.family          = "leaper"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 69
Creature.hp_variance     = 6
Creature.ds_melee        = 19
Creature.ds_bolt         = 9
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 0
Creature.armor_asg       = 5
Creature.armor_natural   = true
Creature.attacks = {
    { type = "bite", as = 94, damage_type = "puncture" },
    { type = "claw", as = 94, damage_type = "slash" },
    { type = "stomp", as = 94, damage_type = "crush" },
}
Creature.spells = {

}
Creature.abilities = { "leap_maneuver" }
Creature.immune    = {  }
Creature.resist    = {}
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a leaper hide"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = { 7707, 7712, 7713, 7714, 7715, 7716, 7717, 7718, 7719, 7720, 7721, 7722, 7723, 7724, 7725 }
Creature.roam_rooms  = { 7707, 7712, 7713, 7714, 7715, 7716, 7717, 7718, 7719, 7720, 7721, 7722, 7723, 7724, 7725 }
Creature.roam_chance     = 20
Creature.respawn_seconds = 220
Creature.max_count       = 6
Creature.description = "The leaper is built entirely around the premise of the first strike: a compact, low body on four heavily-muscled legs that can accelerate from stillness to a full charge in less time than it takes to register the movement. Its hide is tough, its jaw is strong, and it has evidently learned that the stomp delivered at the apex of a leap hits harder than anything else in its arsenal."
return Creature
