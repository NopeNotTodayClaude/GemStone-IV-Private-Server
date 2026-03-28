-- Creature: striped relnak
-- Zone: rambling_meadows / Rambling Meadows  |  Level: 3
-- Source: https://gswiki.play.net/Striped_relnak
-- HP: 42 | AS: 71 (charge), 61 (bite/stomp) | DS: 27-41 (mid ~34) | bolt: ?
-- ASG: 1N natural | TD: 9 | Treasure: no coins, no gems | Skin: relnak hide
local Creature = {}

Creature.id              = 9112
Creature.name            = "striped relnak"
Creature.level           = 3
Creature.family          = "reptilian"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 42
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 34
Creature.ds_bolt         = 18
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "charge", as = 71, damage_type = "crush" },
    { type = "bite",   as = 61, damage_type = "puncture" },
    { type = "stomp",  as = 61, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a striped relnak sail"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Rambling Meadows level-3 area — same rooms as striped_reinak.
-- Relnak is a step up from reinak; they share the same meadow band.
-- Hard cap prevents reaching the level-6 lynx territory to the north.
Creature.spawn_rooms = {
    5970, 5971, 5972, 5973,
    5976, 5977, 5978, 5985,
    5986, 5987, 5988, 5989,
    5990, 5991, 5992, 5993,
}

Creature.roam_rooms = {
    5970, 5971, 5972, 5973,
    5976, 5977, 5978, 5985,
    5986, 5987, 5988, 5989,
    5990, 5991, 5992, 5993,
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 200
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The striped relnak is a low-slung reptilian quadruped marked with vivid bands of dark brown on tawny gold.  Its short legs are deceptive — when it charges, it accelerates with startling speed, and the stomp it delivers with its broad forefeet is the hit that usually breaks things."

return Creature
