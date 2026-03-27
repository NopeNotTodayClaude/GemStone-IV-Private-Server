-- Creature: fel wolf
-- Zone: Lunule Weald / Felwood Grove  |  Level: 17
local Creature = {}
Creature.id              = 9506
Creature.name            = "fel wolf"
Creature.level           = 17
Creature.family          = "canine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 206
Creature.hp_variance     = 15
Creature.ds_melee        = 150
Creature.ds_bolt         = 70
Creature.td_spiritual    = 54
Creature.td_elemental    = 54
Creature.udf             = 8
Creature.armor_asg       = 3
Creature.armor_natural   = true
Creature.attacks = {
    { type="bite", as=196, damage_type="puncture" },
    { type="claw", as=190, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "pack_tactics",
    "fel_poison_bite",
    "howl_of_dread",
}
Creature.immune    = {
    "poison",
}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a fel wolf pelt"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
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
    10578,
    10579,
    10580,
    10581
    }
Creature.roam_rooms = {
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
    10578,
    10579,
    10580,
    10581
    }
Creature.roam_chance     = 22
Creature.respawn_seconds = 360
Creature.max_count       = 2
Creature.description = "The corruption of the Felwood has warped these wolves into something other than natural animals.  The pelt is patchy and dark, with sores that leak a faintly luminous ichor.  The eyes hold a sick yellow glow, and the bite carries a venom derived from the fell energies saturating the grove.  They hunt in packs with the coordinated malice of creatures whose intelligence has been sharpened by corruption rather than dulled."
return Creature
