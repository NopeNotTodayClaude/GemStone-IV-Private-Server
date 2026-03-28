-- Creature: fire salamander
-- Zone: WL Catacombs / Deep  |  Level: 3
local Creature = {}
Creature.id              = 9306
Creature.name            = "fire salamander"
Creature.level           = 3
Creature.family          = "salamander"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 54
Creature.hp_variance     = 5
Creature.ds_melee        = 38
Creature.ds_bolt         = 18
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 3
Creature.armor_asg       = 3
Creature.armor_natural   = true
Creature.attacks = {
    { type="bite", as=56, damage_type="puncture" },
    { type="claw", as=52, damage_type="slash" },
    { type="fire_spit", as=48, damage_type="fire" },
}
Creature.spells = {}
Creature.abilities = {
    "fire_spit",
    "heat_aura",
}
Creature.immune    = {
    "fire",
}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a salamander skin"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    5934,
    5935,
    5936,
    5937,
    5938,
    5939,
    5940,
    5941,
    5942,
    5943,
    5944,
    5945,
    5946,
    5947
    }
Creature.roam_rooms = {
    5934,
    5935,
    5936,
    5937,
    5938,
    5939,
    5940,
    5941,
    5942,
    5943,
    5944,
    5945,
    5946,
    5947,
    5931,
    5932,
    5933
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 200
Creature.max_count       = 2
Creature.description = "Jet black with vivid orange and yellow patterns along its flanks, the fire salamander seems lit from within — the pigment of its markings actually radiating a faint, uncomfortable warmth.  Roughly the size of a large cat, it moves through the deep tunnels with leisurely confidence, leaving faint scorch marks wherever it rests."
return Creature
