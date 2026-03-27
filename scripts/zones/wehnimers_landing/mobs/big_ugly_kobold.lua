-- Creature: big ugly kobold
-- Zone: wehnimers_landing / Kobold Mines (zone 15)  |  Level: 2
-- Source: https://gswiki.play.net/Big_ugly_kobold
-- HP: 50 | AS: 36-62 short sword (mid ~49) | DS: 23-86 (mid ~55) | bolt: 23 | TD: 6
-- ASG: 1N natural | Classification: living | Body: biped
-- Treasure: coins yes, gems yes, boxes yes | Skin: a kobold skin
local Creature = {}

Creature.id              = 9332
Creature.name            = "big ugly kobold"
Creature.level           = 2
Creature.family          = "kobold"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 50
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: short sword 36-62 AS (using 49 midpoint), DS 23-86 (using 55 midpoint)
-- bolt DS 23, TD 6 (empath/elemental confirmed)
Creature.ds_melee        = 55
Creature.ds_bolt         = 23
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "short_sword", as = 49, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = { "kobold_pair_knockdown" }
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a kobold skin"
Creature.special_loot = { "a kobold ear" }

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Kobold Mines — the underground complex west of Wehnimer's Landing.
-- Hard cap to mine rooms; these kobolds do NOT roam into the trollfang.
Creature.spawn_rooms = {
    7999, 8000, 8001, 8002, 8003,
    8004, 8005, 8006, 8007, 8008,
    8009, 8010, 8011, 8012, 8013,
    8014, 8015, 8016, 8017, 8018,
    8019, 8020, 8021,
}

Creature.roam_rooms = {
    7999, 8000, 8001, 8002, 8003,
    8004, 8005, 8006, 8007, 8008,
    8009, 8010, 8011, 8012, 8013,
    8014, 8015, 8016, 8017, 8018,
    8019, 8020, 8021,
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 150
Creature.max_count       = 8

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Larger and considerably uglier than the standard kobold, the big ugly kobold makes up for its lack of subtlety with raw aggression.  Its scales are thicker and more irregular, its teeth more prominent, and its expression more thoroughly hostile.  It carries a short sword with the confidence of something that has been in a great many fights and survived most of them."

return Creature
