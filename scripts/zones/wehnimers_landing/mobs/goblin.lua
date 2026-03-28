-- Creature: goblin
-- Zone: Upper Trollfang / Upper  |  Level: 2
local Creature = {}
Creature.id              = 9401
Creature.name            = "goblin"
Creature.level           = 2
Creature.family          = "goblin"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 42
Creature.hp_variance     = 5
Creature.ds_melee        = 30
Creature.ds_bolt         = 12
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 5
Creature.armor_natural   = false
Creature.attacks = {
    { type="handaxe", as=40, damage_type="slash" },
    { type="spear", as=36, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {
    "scavenge_weapon",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = true
Creature.skin        = "a goblin skin"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    452,
    453,
    454,
    455,
    456,
    457,
    458,
    459,
    460,
    461,
    462,
    463,
    464,
    465,
    466,
    467
    }
Creature.roam_rooms = {
    452,
    453,
    454,
    455,
    456,
    457,
    458,
    459,
    460,
    461,
    462,
    463,
    464,
    465,
    466,
    467,
    468,
    469,
    470,
    471,
    472,
    473,
    474,
    475
    }
Creature.roam_chance     = 30
Creature.respawn_seconds = 160
Creature.max_count       = 3
Creature.description = "Short, green-skinned, and perpetually irritable, the goblin lurks at the edge of the trollfang scrub looking for opportunities to ambush, steal, or simply make someone else's day worse.  Its armor is an implausible combination of scavenged pieces, and its weapons are whatever it found most recently.  It fights with a cowardly viciousness."
return Creature
