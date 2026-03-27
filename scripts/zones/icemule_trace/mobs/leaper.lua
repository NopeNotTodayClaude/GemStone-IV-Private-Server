-- Creature: leaper
-- Zone: icemule_trace / Snowflake Vale (glatoph)  |  Level: 6
-- Source: gswiki.play.net/Leaper
-- HP: 69 | AS: bite/claw/stomp 94 AS | DS: 19 | bolt DS: 9 | TD: 18
-- ASG: 5N | Body: quadruped
-- Treasure: no coins | Skin: a leaper hide
local Creature = {}
Creature.id              = 10420
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
Creature.spawn_rooms = { 2558, 2559, 2560, 2561, 2562, 2563, 2564, 2565, 2566, 2567, 2568, 2569, 2570, 2571, 2572 }
Creature.roam_rooms  = { 2558, 2559, 2560, 2561, 2562, 2563, 2564, 2565, 2566, 2567, 2568, 2569, 2570, 2571, 2572 }
Creature.roam_chance     = 20
Creature.respawn_seconds = 220
Creature.max_count       = 5
Creature.description = "The leaper haunting these frozen slopes is leaner than its coastal cousin, its pale grey hide blending with the rocky snow-dusted terrain. The cold appears to have done nothing to dampen its aggression. It crouches perfectly still until you are close enough that the lunge covers the distance before your response can."
return Creature
