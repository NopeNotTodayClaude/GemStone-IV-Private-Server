-- Creature: relnak
-- Zone: WL Catacombs / Mid Tunnels  |  Level: 3
local Creature = {}
Creature.id              = 9305
Creature.name            = "relnak"
Creature.level           = 3
Creature.family          = "relnak"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 52
Creature.hp_variance     = 5
Creature.ds_melee        = 34
Creature.ds_bolt         = 16
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 0
Creature.armor_asg       = 2
Creature.armor_natural   = false
Creature.attacks = {
    { type="claw", as=54, damage_type="slash" },
    { type="bite", as=50, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a relnak sail"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
-- Rooms 5900-5940 are reserved for fanged_rodent only (Ta'Vaalor catacombs).
-- Assign proper WL catacomb room IDs here when confirmed.
Creature.spawn_rooms = {
    2268, 2269, 2270, 2271, 2272, 2273, 2274, 2275, 2276, 2277, 2278
}
Creature.roam_rooms  = {
    2267, 2268, 2269, 2270, 2271, 2272, 2273, 2274, 2275, 2276, 2277, 2278, 2279, 2280
}
Creature.roam_chance     = 25
Creature.respawn_seconds = 180
Creature.max_count       = 2
Creature.description = "The relnak is an ungainly, bipedal creature about the height of a child, with overlarge hands and a flat, disk-like face dominated by a wide mouth and small, closely-set eyes.  Pale grey-brown skin has the faintly moist quality of cave-dwellers, and it moves with a shuffling gait broken by occasional bursts of surprising speed."
return Creature
