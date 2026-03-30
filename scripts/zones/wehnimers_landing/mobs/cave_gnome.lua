-- Creature: cave gnome
-- Zone: WL Catacombs / Mid Tunnels  |  Level: 2
local Creature = {}
Creature.id              = 9304
Creature.name            = "cave gnome"
Creature.level           = 2
Creature.family          = "gnome"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 42
Creature.hp_variance     = 5
Creature.ds_melee        = 26
Creature.ds_bolt         = 12
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 2
Creature.armor_natural   = false
Creature.attacks = {
    { type="dagger", as=38, damage_type="puncture" },
    { type="thrown_rock", as=32, damage_type="crush" },
}
Creature.spells = {}
Creature.abilities = {
    "cave_sight",
    "hide_in_shadows",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = true
Creature.skin        = "a gnome scalp"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    2268, 2269, 2270, 2271, 2272, 2273, 2274, 7524, 7525, 7526,
    7540, 7542, 7543, 7544, 7545, 7546, 7547, 7550
}
Creature.roam_rooms  = {
    2268, 2269, 2270, 2271, 2272, 2273, 2274, 7524, 7525, 7526,
    7540, 7542, 7543, 7544, 7545, 7546, 7547, 7550
}
Creature.roam_chance     = 25
Creature.respawn_seconds = 160
Creature.max_count       = 2
Creature.description = "Pallid and nearly sightless from generations of cave-dwelling, the cave gnome has adapted its mischievous gnomish nature to the underground environment.  Enormous cloudy eyes gather ambient light with surprising efficiency, and long fingers end in tough nails suited for scrabbling through stone.  It carries crude tools that serve as weapons and a small pack of scavenged oddities."
return Creature
