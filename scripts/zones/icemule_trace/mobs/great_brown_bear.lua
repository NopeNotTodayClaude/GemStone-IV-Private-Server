-- Creature: great brown bear
-- Zone: Icemule Trace / Glatoph  |  Level: 14
local Creature = {}
Creature.id              = 10305
Creature.name            = "great brown bear"
Creature.level           = 14
Creature.family          = "bear"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 178
Creature.hp_variance     = 14
Creature.ds_melee        = 128
Creature.ds_bolt         = 58
Creature.td_spiritual    = 46
Creature.td_elemental    = 46
Creature.udf             = 5
Creature.armor_asg       = 7
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=175, damage_type="slash" },
    { type="bite", as=168, damage_type="puncture" },
    { type="bear_hug", as=162, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "bear_maul",
    "toughskin",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = "a brown bear skin"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    2558,
    2559,
    2560,
    2561,
    2562,
    2563,
    2564,
    2565,
    2566,
    2567,
    2568,
    2569,
    2570,
    2571,
    3550,
    3551,
    3552,
    3553,
    3554,
    3559,
    3617
    }
Creature.roam_rooms      = {
    2558,
    2559,
    2560,
    2561,
    2562,
    2563,
    2564,
    2565,
    2566,
    2567,
    2568,
    2569,
    2570,
    2571,
    3550,
    3551,
    3552,
    3553,
    3554,
    3559,
    3617
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 320
Creature.max_count       = 3
Creature.description     = "The great brown bears of Glatoph are unusually large even by the standards of the species, driven by the need to carry enough fat reserves to survive the extreme cold of the deep interior.  The fur is thick and coarse, ranging from dark brown to near-black in winter coat.  They are not inherently aggressive but will defend territory and food sources with genuine commitment."
return Creature
