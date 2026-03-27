-- Creature: Darkwoode
-- Zone: Upper Trollfang / Sentoph  |  Level: 13
local Creature = {}
Creature.id              = 9408
Creature.name            = "Darkwoode"
Creature.level           = 13
Creature.family          = "darkwoode"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 160
Creature.hp_variance     = 12
Creature.ds_melee        = 140
Creature.ds_bolt         = 65
Creature.td_spiritual    = 46
Creature.td_elemental    = 46
Creature.udf             = 130
Creature.armor_asg       = 8
Creature.armor_natural   = false
Creature.attacks = {
    { type="claw", as=165, damage_type="slash" },
    { type="bite", as=158, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {
    "disease_touch",
    "ghoul_rot_chance",
    "fear_aura",
}
Creature.immune    = {
    "disease",
    "poison",
}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a darkwoode talon"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    6821,
    6822,
    6823,
    6824,
    6825,
    6826,
    6827,
    6828,
    7780,
    7781,
    7782,
    7783
    }
Creature.roam_rooms = {
    6821,
    6822,
    6823,
    6824,
    6825,
    6826,
    6827,
    6828,
    7780,
    7781,
    7782,
    7783,
    7784,
    7785,
    7786,
    7787,
    7788
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 360
Creature.max_count       = 1
Creature.description = "Resembling a warped, animate tree-stump with too many limbs, the Darkwoode shambles through the sentoph brush on roots that serve as legs.  Bark-like skin covers a frame that is wholly wrong in its proportions, and the face — if it can be called that — is a knotted mass of wood-grain with hollow, lightless eye sockets.  Its origin lies in a dark union of fell magic and old-growth timber."
return Creature
