-- Creature: black-winged daggerbeak
-- Zone: solhaven / Solhaven Environs (Coastal Cliffs)  |  Level: 1
-- Source: https://gswiki.play.net/Black-winged_daggerbeak
-- HP: 28 | AS: 36 (bite) | DS: 27 | TD: 3 | ASG: 1N (natural)
-- Treasure: no coins, no gems, no magic, no boxes | Skin: a daggerbeak wing
local Creature = {}

Creature.id              = 10116
Creature.name            = "black-winged daggerbeak"
Creature.level           = 1
Creature.family          = "bird"
Creature.classification  = "living"
Creature.body_type       = "avian"

Creature.hp_base         = 28
Creature.hp_variance     = 4

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: bite 36 AS, DS 27, bolt DS 25, UDF 32, TD 3 all schools
Creature.ds_melee        = 27
Creature.ds_bolt         = 25
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 32
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 36, damage_type = "puncture" },
}

Creature.spells   = {}
Creature.abilities = {}
Creature.immune   = {}
Creature.resist   = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: no coins, no gems, no magic, no boxes. Skin only.
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a daggerbeak wing"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Coastal Cliffs lower area (Solhaven Environs), same block as level-1 kobold.
-- Hard boundary matches kobold to keep both contained to the entry-level area.
Creature.spawn_rooms = {
    478, 479, 480, 481, 482,
    483, 484, 485, 486, 487,
    488, 489, 490, 491, 492, 493,
}

Creature.roam_rooms = {
    478, 479, 480, 481, 482,
    483, 484, 485, 486, 487,
    488, 489, 490, 491, 492, 493,
}

Creature.roam_chance     = 35
Creature.respawn_seconds = 150
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "With its naked head resembling that of a vulture and a wingspan of almost three feet, the black-winged daggerbeak gets its name from its wickedly pointed beak and the way it uses it.  Created by a mean-spirited enchanter for the bedevilment of some peasants who had offended him, the daggerbeak survives by stabbing domesticated herd animals with its beak and drinking their blood."

return Creature
