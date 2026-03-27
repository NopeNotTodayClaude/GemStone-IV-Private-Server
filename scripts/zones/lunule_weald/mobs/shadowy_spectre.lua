-- Creature: shadowy spectre
-- Zone: Lunule Weald / Zealot Village  |  Level: 25
local Creature = {}
Creature.id              = 9511
Creature.name            = "shadowy spectre"
Creature.level           = 25
Creature.family          = "spectre"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 282
Creature.hp_variance     = 19
Creature.ds_melee        = 210
Creature.ds_bolt         = 100
Creature.td_spiritual    = 80
Creature.td_elemental    = 58
Creature.udf             = 298
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks = {
    { type="spectral_touch", as=260, damage_type="unbalancing" },
    { type="spirit_rend", as=252, damage_type="cold" },
    { type="terror_wave", as=245, damage_type="unbalancing" },
}
Creature.spells = {
    { name="spirit_slayer", cs=140, as=0 },
    { name="terror", cs=135, as=0 },
}
Creature.abilities = {
    "spirit_strike",
    "fear_aura",
    "phase_through_terrain",
    "shadow_meld",
    "soul_drain",
}
Creature.immune    = {
    "disease",
    "poison",
    "cold",
    "electricity",
}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = ""
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = "shatters into fragments of shadow and darkness."
Creature.spawn_rooms = {
    10605,
    10606,
    10607,
    10608,
    10609,
    10611,
    10612,
    10613,
    10614,
    10615,
    10616,
    10617
    }
Creature.roam_rooms = {
    10605,
    10606,
    10607,
    10608,
    10609,
    10611,
    10612,
    10613,
    10614,
    10615,
    10616,
    10617
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 600
Creature.max_count       = 1
Creature.description = "Where the dark apparition is shadow given shape, the shadowy spectre is something older and more refined — a distillation of whatever terrible will animates the corrupted dead.  It communicates in feelings rather than sounds: waves of cold dread, images of ending, the specific terror of being seen by something that does not recognize your right to exist.  Its passage leaves frost on every surface."
return Creature
