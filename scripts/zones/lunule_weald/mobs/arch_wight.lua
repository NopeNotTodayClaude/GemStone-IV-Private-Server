-- Creature: arch wight
-- Zone: Lunule Weald / Perish Glen  |  Level: 21
local Creature = {}
Creature.id              = 9509
Creature.name            = "arch wight"
Creature.level           = 21
Creature.family          = "wight"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 242
Creature.hp_variance     = 17
Creature.ds_melee        = 178
Creature.ds_bolt         = 85
Creature.td_spiritual    = 67
Creature.td_elemental    = 67
Creature.udf             = 258
Creature.armor_asg       = 12
Creature.armor_natural   = false
Creature.attacks = {
    { type="claw", as=223, damage_type="slash" },
    { type="bite", as=216, damage_type="puncture" },
    { type="life_drain", as=210, damage_type="cold" },
}
Creature.spells = {
    { name="wither", cs=122, as=0 },
    { name="dark_catalyst", cs=118, as=0 },
}
Creature.abilities = {
    "wight_drain",
    "life_drain",
    "disease_touch",
    "aura_of_dread",
}
Creature.immune    = {
    "disease",
    "poison",
}
Creature.resist    = {
    "cold",
}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a wight finger bone"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    10589,
    10590,
    10591,
    10592,
    10593,
    10594,
    10595,
    10610,
    10597,
    10598,
    10599
    }
Creature.roam_rooms = {
    10589,
    10590,
    10591,
    10592,
    10593,
    10594,
    10595,
    10610,
    10597,
    10598,
    10599
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 540
Creature.max_count       = 1
Creature.description = "The arch wight stands at the apex of wighthood — ancient, powerful, and saturated with the necromantic energies that sustain it.  What was once a figure of some authority in life retains vestiges of that bearing in the upright posture and deliberate movement.  The grey, papery flesh clings tightly to the skull, and the eyes hold the steady glow of old embers.  Its very presence drains warmth from the air."
return Creature
