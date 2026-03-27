-- Creature: slimy little grub
-- Zone: wehntoph / Twin Canyons  |  Level: 1
-- Source: https://gswiki.play.net/Slimy_little_grub
-- HP: 28 | AS: 47 (stinger) | DS: 22-56 (mid ~39) | bolt: 25 | ASG: 1N natural | TD: 3
-- Treasure: no coins, no gems, no boxes, no skin
-- Note: gremlins eat these (ambient event hook)
local Creature = {}

Creature.id              = 10411
Creature.name            = "slimy little grub"
Creature.level           = 1
Creature.family          = "worm"
Creature.classification  = "living"
Creature.body_type       = "worm"

Creature.hp_base         = 28
Creature.hp_variance     = 4

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: stinger 47 AS, DS 22-56 (using 39 midpoint), bolt 25, ASG 1N, TD 3
Creature.ds_melee        = 39
Creature.ds_bolt         = 25
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "sting", as = 47, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: no coins, no gems, no boxes, no skin
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = ""
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 120
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Wehntoph lower canyon rooms. Hard cap — these grubs do not climb out
-- of the canyon floor to reach the higher rocky areas (krag slopes).
Creature.spawn_rooms = {
    6110, 6111, 6112, 6113,
    6114, 6115, 6116, 6117, 6118,
}

Creature.roam_rooms = {
    6110, 6111, 6112, 6113,
    6114, 6115, 6116, 6117, 6118,
}

Creature.roam_chance     = 15
Creature.respawn_seconds = 100
Creature.max_count       = 12

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The little grub is a small yellowish white creature little more than six inches long.  It is covered in a sickly green slime that leaves a trail behind it.  Somehow, despite being nearly featureless, it manages to convey a sense of singular malevolent intent."

return Creature
