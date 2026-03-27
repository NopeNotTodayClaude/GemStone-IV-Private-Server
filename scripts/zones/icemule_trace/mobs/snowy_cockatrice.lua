-- Creature: snowy cockatrice
-- Zone: icemule_trace / Snowflake Vale (glatoph lower)  |  Level: 6
-- Source: gswiki.play.net/Snowy_cockatrice
-- HP: 69 | AS: charge 109 / claw/pincer 99 AS | DS: 38 | bolt DS: 31 | TD: 18
-- ASG: 8N | Body: hybrid
-- Treasure: no coins | Skin: a snowy cockatrice feather
local Creature = {}
Creature.id              = 10422
Creature.name            = "snowy cockatrice"
Creature.level           = 6
Creature.family          = "basilisk"
Creature.classification  = "living"
Creature.body_type       = "hybrid"
Creature.hp_base         = 69
Creature.hp_variance     = 6
Creature.ds_melee        = 38
Creature.ds_bolt         = 31
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 0
Creature.armor_asg       = 8
Creature.armor_natural   = true
Creature.attacks = {
    { type = "charge", as = 109, damage_type = "crush" },
    { type = "claw", as = 99, damage_type = "slash" },
    { type = "pincer", as = 99, damage_type = "crush" },
}
Creature.spells = {

}
Creature.abilities = { "stare_roundtime" }
Creature.immune    = {  }
Creature.resist    = {}
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a snowy cockatrice feather"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = { 2570, 2571, 2572, 2573, 2574, 2575, 2576, 2577, 2578, 2579, 2580, 2581, 2582, 2583, 2584 }
Creature.roam_rooms  = { 2570, 2571, 2572, 2573, 2574, 2575, 2576, 2577, 2578, 2579, 2580, 2581, 2582, 2583, 2584 }
Creature.roam_chance     = 20
Creature.respawn_seconds = 240
Creature.max_count       = 5
Creature.description = "The snowy cockatrice has adapted to frozen terrain by developing a coat of stiff white feathers over its already-formidable frame. The leonine hindquarters provide the charge; the rooster head on the serpent neck provides the stare — a focused, petrifying gaze that costs its target precious seconds of reaction time. It uses those seconds well."
return Creature
