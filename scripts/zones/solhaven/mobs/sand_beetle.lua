-- Creature: sand beetle
-- Zone: Vornavis / North Beach Lagoon  |  Level: 33
local Creature = {}
Creature.id              = 10113
Creature.name            = "sand beetle"
Creature.level           = 33
Creature.family          = "insect"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 425
Creature.hp_variance     = 35
Creature.ds_melee        = 272
Creature.ds_bolt         = 132
Creature.td_spiritual    = 108
Creature.td_elemental    = 108
Creature.udf             = 5
Creature.armor_asg       = 15
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=330, damage_type="puncture" },
    { type="claw", as=322, damage_type="slash" },
    { type="shell_ram", as=315, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "armoured_shell",
    "burrowing_escape",
    "shell_ram",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a beetle carapace plate"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    7638,
    7639,
    7640,
    7641,
    7642,
    7643,
    7644,
    7654
    }
Creature.roam_rooms      = {
    7638,
    7639,
    7640,
    7641,
    7642,
    7643,
    7644,
    7654
    }
Creature.roam_chance     = 10
Creature.respawn_seconds = 480
Creature.max_count       = 1
Creature.description     = "Near the size of a small cart, the sand beetle has a carapace of iridescent blue-black chitin so thick it has defeated weapons that would cut through plate armour.  The mandibles at the front, designed for digging in sand, are incidentally also excellent weapons.  It moves with the deliberate, unstoppable quality of something that has never needed to hurry because nothing it has encountered has ever been fast enough to matter."
return Creature
