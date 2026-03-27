-- Creature: lesser frost shade
-- Zone: icemule_trace / Snowy Forest (Icemule Environs)  |  Level: 2
-- Source: https://gswiki.play.net/Lesser_frost_shade
-- HP: 44 | AS: 43 (handaxe) | CS: 10 (Calm 201), 14 (Repel)
-- DS: 3 melee | bolt DS: ? (using 3) | TD: 6 | ASG: 5 (light leather)
-- Classification: non-corporeal undead, element-based (cold)
-- Treasure: coins ?, gems ?, boxes ? — using yes for all per ghost family standard
local Creature = {}

Creature.id              = 10320
Creature.name            = "lesser frost shade"
Creature.level           = 2
Creature.family          = "ghost"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 44
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: handaxe 43 AS, Calm (201) CS 10, Repel CS 14
-- DS 3 melee (only confirmed value), TD 6 confirmed for cleric/sorcerer/elemental
Creature.ds_melee        = 3
Creature.ds_bolt         = 3
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 5
Creature.armor_natural   = false

Creature.attacks = {
    { type = "handaxe", as = 43, damage_type = "slash" },
}

Creature.spells = {
    { name = "Calm (201)", cs = 10, as = 0 },
    { name = "Repel",      cs = 14, as = 0 },
}

Creature.abilities = {
    "cold_aura",   -- element-based cold damage on contact
}

Creature.immune = {
    "disease",
    "poison",
    "cold",
}

Creature.resist = {
    "pierce",
    "slash",
    "crush",
}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Ghost family standard: coins yes, gems yes, magic yes, boxes yes. No skin.
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = ""
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 60
Creature.crumbles      = true
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Icemule Snowy Forest — same entry rooms as rolton/kobold/rabid squirrel.
-- Frost shades do not drift to glatoph (hard cap here).
Creature.spawn_rooms = {
    3195, 3196, 3197, 3198,
    3199, 3200, 3201, 3202,
    3203, 3204, 3205, 3206,
}

Creature.roam_rooms = {
    3195, 3196, 3197, 3198,
    3199, 3200, 3201, 3202,
    3203, 3204, 3205, 3206,
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 180
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Barely distinguishable from the snow and mist around it, the lesser frost shade is a dim silhouette of cold blue-white light.  The temperature drops noticeably as it drifts closer.  It wields a handaxe of pure ice that looks real enough and swings like it."

return Creature
