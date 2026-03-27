-- Creature: nasty little gremlin
-- Zone: wehntoph / Twin Canyons  |  Level: 5
-- Source: https://gswiki.play.net/Nasty_little_gremlin
-- HP: 80 | AS: 95 (dagger) | DS: 22-91 (mid ~57) | bolt: 30 | UDF: 96 | TD: 10-11
-- ASG: 1N natural | Classification: living | Body: biped
-- Treasure: coins yes, gems yes, magic yes, boxes yes | No skin
local Creature = {}

Creature.id              = 10413
Creature.name            = "nasty little gremlin"
Creature.level           = 5
Creature.family          = "gremlin"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 80
Creature.hp_variance     = 7

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: dagger 95 AS, DS 22-91 (using 57 midpoint), bolt 30, UDF 96
-- TD: bard base 10, sorc base 11, minor elemental 10, major elemental 10,
--     minor spiritual 10 — using 10-11 range, set to 15 standard L5
Creature.ds_melee        = 57
Creature.ds_bolt         = 30
Creature.td_spiritual    = 15
Creature.td_elemental    = 15
Creature.udf             = 96
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "dagger", as = 95, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = { "steal_item", "gremlin_eat_grub" }
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = ""
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Wehntoph upper canyon area — gremlins range further up the canyon walls
-- than the grubs, sharing some territory but primarily in the mid-canyon.
-- Hard cap prevents them reaching the Krag Slopes (zone 103).
Creature.spawn_rooms = {
    6110, 6111, 6112, 6113,
    6114, 6115, 6116, 6117, 6118,
    7917, 7918, 7919, 7920, 7921,
}

Creature.roam_rooms = {
    6110, 6111, 6112, 6113,
    6114, 6115, 6116, 6117, 6118,
    7917, 7918, 7919, 7920, 7921,
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 200
Creature.max_count       = 8

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The little gremlin is a small furless creature with beady little eyes and sharp teeth that have been filed into triangular points.  Its eyes are a vivid red, and its oversized ears are scarred from countless fights.  It carries a dagger in one clawed hand and something it just stole in the other, and it darts from shadow to shadow with manic, infuriating speed."

return Creature
