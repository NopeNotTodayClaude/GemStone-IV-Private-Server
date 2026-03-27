-- Creature: whiptail
-- Zone: solhaven / Vornavian Coast  |  Level: 4
-- Source: https://gswiki.play.net/Whiptail
-- HP: 50 | AS: 65 (impale + pincer) | DS: 29 | bolt: 26 | TD: 12
-- ASG: 12N (brigandine, natural) | Classification: living | Body: arachnid
-- Special: web ability (immobilize)
-- Treasure: no coins, no gems, no magic, no boxes | Skin: a whiptail stinger
local Creature = {}

Creature.id              = 10124
Creature.name            = "whiptail"
Creature.level           = 4
Creature.family          = "arachnid"
Creature.classification  = "living"
Creature.body_type       = "arachnid"

Creature.hp_base         = 50
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: impale 65 AS, pincer 65 AS, DS 29, bolt 26, TD 12
-- ASG 12N (brigandine natural) — heavily armored for its level
Creature.ds_melee        = 29
Creature.ds_bolt         = 26
Creature.td_spiritual    = 12
Creature.td_elemental    = 12
Creature.udf             = 0
Creature.armor_asg       = 12
Creature.armor_natural   = true

Creature.attacks = {
    { type = "pincer", as = 65, damage_type = "crush" },
    { type = "charge", as = 65, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = {
    "web_immobilize",
}

Creature.immune = {}
Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: no coins, no gems, no magic, no boxes. Skin only.
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a whiptail stinger"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Vornavian Coast — shares the mid-cliffs area with cobra, mongrel kobold,
-- and urgh. The whiptail's natural armor and web make it the toughest
-- creature at this level range. Hard cap to the coastal cliffs band;
-- it does not drift toward the upper cliffs or caverns.
Creature.spawn_rooms = {
    7601,
    7673, 7674, 7675, 7676,
    7677, 7678, 7679, 7680, 7681,
}

Creature.roam_rooms = {
    7601,
    7673, 7674, 7675, 7676,
    7677, 7678, 7679, 7680, 7681,
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 240
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The whiptail's body is squat and heavily plated, its natural armor shrugging off most blows with an ugly grinding sound.  The tail that gives it its name is thin, whip-fast, and tipped with a barbed stinger it uses to immobilize prey before the pincers close.  It scuttles sideways with surprising speed for something built like a small fortress."

return Creature
