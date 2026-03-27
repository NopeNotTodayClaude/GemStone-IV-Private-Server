-- Creature: cave nipper
-- Zone: wehnimers_landing / Abandoned Mine (rooms 2261-2282)  |  Level: 3
-- Source: GUESSED - balanced vs L3 cave creatures
-- HP: 44 | AS: bite 65 AS (guessed) | DS: 42 | bolt DS: 22 | TD: 9
-- ASG: 5N (natural) | Body: quadruped
-- Treasure: no coins | Skin: a cave nipper skin
local Creature = {}

Creature.id              = 9334
Creature.name            = "cave nipper"
Creature.level           = 3
Creature.family          = "reptilian"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 44
Creature.hp_variance     = 4

Creature.ds_melee        = 42
Creature.ds_bolt         = 22
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 60
Creature.armor_asg       = 5
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 65, damage_type = "puncture" },
    { type = "claw", as = 58, damage_type = "slash" },
}

Creature.spells = {

}
Creature.abilities = {  }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a cave nipper skin"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = { 2261, 2262, 2263, 2264, 2265, 2266, 2267, 2268, 2269, 2270, 2271, 2272, 2273, 2274, 2275, 2276, 2277, 2278, 2279, 2280 }
Creature.roam_rooms  = { 2261, 2262, 2263, 2264, 2265, 2266, 2267, 2268, 2269, 2270, 2271, 2272, 2273, 2274, 2275, 2276, 2277, 2278, 2279, 2280 }
Creature.roam_chance     = 20
Creature.respawn_seconds = 180
Creature.max_count       = 7

Creature.description = "The cave nipper is a compact, low-slung reptile with shovel-shaped claws adapted for burrowing through soft rock and packed earth. Its scales are translucent pink-white from generations in lightless mines, and its eyes are vestigial — it hunts entirely by vibration, heat, and an unerring sense of where the air is slightly warmer than the stone."

return Creature
