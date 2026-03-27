-- Creature: decaying woodsman
-- Zone: Lunule Weald / Felwood Grove  |  Level: 15
local Creature = {}
Creature.id              = 9505
Creature.name            = "decaying woodsman"
Creature.level           = 15
Creature.family          = "zombie"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 184
Creature.hp_variance     = 14
Creature.ds_melee        = 127
Creature.ds_bolt         = 60
Creature.td_spiritual    = 49
Creature.td_elemental    = 49
Creature.udf             = 162
Creature.armor_asg       = 6
Creature.armor_natural   = false
Creature.attacks = {
    { type="axe", as=179, damage_type="slash" },
    { type="claw", as=172, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "disease_touch",
    "infectious_bite",
    "woodsman_heft",
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
Creature.skin        = "a woodsman axe handle"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    10547,
    10559,
    10560,
    10561,
    10562,
    10563,
    10564,
    10565,
    10566,
    10567,
    10568,
    10569,
    10570,
    10571,
    10572,
    10573,
    10574,
    10575,
    10576,
    10577
    }
Creature.roam_rooms = {
    10547,
    10559,
    10560,
    10561,
    10562,
    10563,
    10564,
    10565,
    10566,
    10567,
    10568,
    10569,
    10570,
    10571,
    10572,
    10573,
    10574,
    10575,
    10576,
    10577,
    10554,
    10555,
    10578,
    10579,
    10580
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 360
Creature.max_count       = 3
Creature.description = "The decaying woodsman still carries the tools of its former trade — an axe or maul that it swings with the muscle-memory of long practice, even in undeath.  The corruption of the Felwood has done its work on the flesh, leaving patches of exposed bone and blackened, dead tissue beneath the remnants of a logger's work clothes.  It navigates the dark grove with unsettling familiarity."
return Creature
