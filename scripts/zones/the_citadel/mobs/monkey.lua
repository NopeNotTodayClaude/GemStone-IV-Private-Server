-- Creature: monkey
-- Zone: the_citadel / River Tunnels  |  Level: 6
-- Source: gswiki.play.net/Monkey
-- HP: 60 | AS: fist 88/bite 78/cane 70 AS | DS: 48 | bolt DS: 30 | TD: 18
-- ASG: 1N | Body: biped
-- Treasure: coins+boxes | Skin: a monkey paw
local Creature = {}
Creature.id              = 10421
Creature.name            = "monkey"
Creature.level           = 6
Creature.family          = "primate"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 60
Creature.hp_variance     = 6
Creature.ds_melee        = 48
Creature.ds_bolt         = 30
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 80
Creature.armor_asg       = 1
Creature.armor_natural   = true
Creature.attacks = {
    { type = "punch", as = 88, damage_type = "crush" },
    { type = "bite", as = 78, damage_type = "puncture" },
    { type = "club", as = 70, damage_type = "crush" },
}
Creature.spells = {

}
Creature.abilities = { "hide", "taunt" }
Creature.immune    = {  }
Creature.resist    = {}
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a monkey paw"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = { 11151, 11152, 11153, 11154, 11155, 11156, 11157, 11158, 11159, 11160, 11161, 11162, 11163, 11164, 11165 }
Creature.roam_rooms  = { 11151, 11152, 11153, 11154, 11155, 11156, 11157, 11158, 11159, 11160, 11161, 11162, 11163, 11164, 11165 }
Creature.roam_chance     = 20
Creature.respawn_seconds = 200
Creature.max_count       = 7
Creature.description = "The monkey is barely two feet tall and completely convinced this gives it an advantage. It moves with erratic, unpredictable speed through the tunnel complex, armed with a wooden cane it swings with surprising force and a red vine it uses as a whip. It will steal your focus, vanish into the shadows, and reappear hitting you from a direction you weren't watching."
return Creature
