-- Creature: thyril
-- Zone: WL Catacombs  |  Level: 2
local Creature = {}
Creature.id              = 9302
Creature.name            = "thyril"
Creature.level           = 2
Creature.family          = "thyril"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 44
Creature.hp_variance     = 5
Creature.ds_melee        = 32
Creature.ds_bolt         = 14
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 3
Creature.armor_asg       = 1
Creature.armor_natural   = true
Creature.attacks = {
    { type="claw", as=36, damage_type="slash" },
    { type="bite", as=32, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {
    "evade_maneuver",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a thyril pelt"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
-- Rooms 5900-5940 are reserved for fanged_rodent only (Ta'Vaalor catacombs).
-- Assign proper WL catacomb room IDs here when confirmed.
Creature.spawn_rooms = {
    7491, 7492, 7493, 7494, 7532, 7533, 7534, 7535, 7536, 7537
}
Creature.roam_rooms  = {
    7491, 7492, 7493, 7494, 7532, 7533, 7534, 7535, 7536, 7537
}
Creature.roam_chance     = 30
Creature.respawn_seconds = 160
Creature.max_count       = 2
Creature.description = "A young thyril has claimed a territory among the upper catacombs, finding the enclosed space and abundance of smaller prey entirely to its liking.  It moves with fluid silence through the tunnels, its spotted coat oddly effective even against bare stone.  The oversized ears swivel constantly toward any sound."
return Creature
