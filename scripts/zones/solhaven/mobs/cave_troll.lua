-- Creature: cave troll
-- Zone: Vornavis / North Beach Caverns  |  Level: 16
local Creature = {}
Creature.id              = 10110
Creature.name            = "cave troll"
Creature.level           = 16
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 200
Creature.hp_variance     = 16
Creature.ds_melee        = 140
Creature.ds_bolt         = 66
Creature.td_spiritual    = 51
Creature.td_elemental    = 51
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=192, damage_type="slash" },
    { type="bite", as=185, damage_type="puncture" },
    { type="pound", as=178, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "troll_regeneration",
    "cave_sight",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a troll scalp"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    7707,
    7712,
    7713,
    7714,
    7715,
    7716,
    7717,
    7718,
    7719,
    7720,
    7721,
    7722,
    7723,
    7724,
    7725,
    7726,
    7727,
    7728,
    7729,
    7730,
    7731,
    7732,
    7733,
    7734,
    7735,
    7736,
    7737,
    7738
    }
Creature.roam_rooms      = {
    7707,
    7712,
    7713,
    7714,
    7715,
    7716,
    7717,
    7718,
    7719,
    7720,
    7721,
    7722,
    7723,
    7724,
    7725,
    7726,
    7727,
    7728,
    7729,
    7730,
    7731,
    7732,
    7733,
    7734,
    7735,
    7736,
    7737,
    7738
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 360
Creature.max_count       = 4
Creature.description     = "Pale from a life underground, the cave troll has the long arms and hunched posture of something that spends most of its time in low-ceilinged spaces.  The eyes are proportionally larger than those of surface trolls, adapted for dim light, and gleam with a faint luminescence.  The regenerative capability is intact and the size is still formidable; the paleness is the only thing about it that could be called diminished."
return Creature
