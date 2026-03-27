-- Creature: Nedum Vereri
-- Zone: Upper Trollfang / Temple of Love  |  Level: 18
local Creature = {}
Creature.id              = 9415
Creature.name            = "Nedum Vereri"
Creature.level           = 18
Creature.family          = "spirit"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 215
Creature.hp_variance     = 15
Creature.ds_melee        = 165
Creature.ds_bolt         = 80
Creature.td_spiritual    = 60
Creature.td_elemental    = 42
Creature.udf             = 225
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks = {
    { type="spectral_touch", as=202, damage_type="unbalancing" },
    { type="mind_rend", as=196, damage_type="unbalancing" },
}
Creature.spells = {
    { name="mind_shatter", cs=102, as=0 },
    { name="fear_wave", cs=98, as=0 },
}
Creature.abilities = {
    "spirit_strike",
    "fear_aura",
    "mind_blast",
    "phase_through_terrain",
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
Creature.loot_boxes  = false
Creature.skin        = ""
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = "collapses into itself with a sound like breaking glass."
Creature.spawn_rooms = {
    4263,
    4264,
    7800,
    7801,
    7802
    }
Creature.roam_rooms = {
    4263,
    4264,
    7800,
    7801,
    7802,
    6821,
    6822,
    6823
    }
Creature.roam_chance     = 8
Creature.respawn_seconds = 600
Creature.max_count       = 1
Creature.description = "Something terrible once worshipped in the Temple of Love has left its mark on these grounds in the form of the Nedum Vereri — roughly translatable as 'the truly feared.'  It has no solid form, appearing instead as a shifting arrangement of distorted faces and reaching hands barely contained within a vaguely humanoid silhouette.  The psychic pressure of its presence alone is enough to cloud the mind."
return Creature
