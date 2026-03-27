-- Creature: spotted gak
-- Zone: wehnimers_landing / Wehnimer's Environs (Upper Trollfang entry)  |  Level: 2
-- Source: https://gswiki.play.net/Spotted_gak
-- HP: 70 | AS: 48 (impale) | DS: 26 melee / 18 bolt | UDF: 60 | TD: 6
-- ASG: 6N (full leather, natural) | Classification: living | Body: quadruped
-- Treasure: no coins, no gems, no magic, no boxes | Skin: a gak hide
local Creature = {}

Creature.id              = 9321
Creature.name            = "spotted gak"
Creature.level           = 2
Creature.family          = "bovine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 70
Creature.hp_variance     = 6

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: impale 48 AS, DS 26, bolt 18, UDF 60, TD 6 (elemental / spiritual partial)
Creature.ds_melee        = 26
Creature.ds_bolt         = 18
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 60
Creature.armor_asg       = 6
Creature.armor_natural   = true

Creature.attacks = {
    { type = "charge", as = 48, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: no coins, no gems, no magic, no boxes. Skin: a gak hide.
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a gak hide"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Upper Trollfang entry area (Wehnimer's Environs) — same open-terrain
-- rooms as the goblin. Gaks roam the scrub alongside the trollfang entry
-- level mobs. Hard-capped here; they do NOT reach the deeper trollfang
-- or the graveyard zone.
Creature.spawn_rooms = {
    452, 453, 454, 455,
    456, 457, 458, 459,
    460, 461, 462, 463,
    464, 465, 466, 467,
}

Creature.roam_rooms = {
    452, 453, 454, 455,
    456, 457, 458, 459,
    460, 461, 462, 463,
    464, 465, 466, 467,
    468, 469, 470, 471,
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 150
Creature.max_count       = 3

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The spotted gak is a big, ugly beast with a heavy spotted brown pelt.  A marked odor of dung and musk precedes it by some distance, and its thick hide and powerful hindquarters make it look like something that decided being a bull wasn't ambitious enough.  It paws the earth and fixes you with one dim, hostile eye."

return Creature
