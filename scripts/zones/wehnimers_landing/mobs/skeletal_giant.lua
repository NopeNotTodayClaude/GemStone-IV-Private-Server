-- Creature: skeletal giant
-- Zone: Upper Trollfang / Obsidian Tower  |  Level: 33
local Creature = {}
Creature.id              = 9416
Creature.name            = "skeletal giant"
Creature.level           = 33
Creature.family          = "giant"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 435
Creature.hp_variance     = 25
Creature.ds_melee        = 275
Creature.ds_bolt         = 132
Creature.td_spiritual    = 110
Creature.td_elemental    = 110
Creature.udf             = 380
Creature.armor_asg       = 15
Creature.armor_natural   = false
Creature.attacks = {
    { type="greatclub", as=342, damage_type="crush" },
    { type="stomp", as=335, damage_type="crush" },
    { type="throw_boulder", as=320, damage_type="crush" },
}
Creature.spells = {}
Creature.abilities = {
    "giant_stomp",
    "bone_shard_spray",
    "undead_resilience",
}
Creature.immune    = {
    "disease",
    "poison",
    "cold",
}
Creature.resist    = {
    "pierce",
    "slash",
}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a giant bone fragment"
Creature.special_loot = {
    "a massive finger bone",
}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    7756,
    7757,
    7758,
    7759,
    7760,
    7761,
    7762,
    7763,
    7764,
    7765,
    7766,
    7767,
    7768,
    7769,
    7770,
    7771,
    7772,
    7773,
    7774
    }
Creature.roam_rooms = {
    7756,
    7757,
    7758,
    7759,
    7760,
    7761,
    7762,
    7763,
    7764,
    7765,
    7766,
    7767,
    7768,
    7769,
    7770,
    7771,
    7772,
    7773,
    7774
    }
Creature.roam_chance     = 5
Creature.respawn_seconds = 900
Creature.max_count       = 2
Creature.description = "Thirty feet of animated bone tower above you, the skeletal giant's skull housing two cold points of violet light where eyes should be.  Every joint in the massive frame grinds with a sound like millstones, and the impact of each footstep sends visible vibrations through the ground.  Weapons that would slay a man outright barely scratch the ancient bones."
return Creature
