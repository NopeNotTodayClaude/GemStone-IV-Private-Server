-- Creature: ghost
-- Zone: solhaven / Solhaven Environs (Coastal Cliffs)  |  Level: 2
-- Source: https://gswiki.play.net/Ghost
-- HP: 51 | AS: 58 (short sword) | DS: -2 melee / -13 bolt | UDF: 48 | TD: 6
-- ASG: 1N (natural) | Classification: non-corporeal undead
-- Treasure: coins yes, gems yes, magic ?, boxes yes | No skin
local Creature = {}

Creature.id              = 10118
Creature.name            = "ghost"
Creature.level           = 2
Creature.family          = "ghost"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 51
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: short sword 58 AS, DS -2 melee, bolt -13, UDF 48, TD 6 all schools
Creature.ds_melee        = -2
Creature.ds_bolt         = -13
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 48
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "short_sword", as = 58, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = {}

Creature.immune = {
    "disease",
    "poison",
}

Creature.resist = {
    "pierce",
    "slash",
    "crush",
}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: coins yes, gems yes, boxes yes. No skin.
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = ""
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 60    -- non-corporeal fade faster
Creature.crumbles      = true
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Coastal Cliffs lower area (Solhaven Environs).
-- Shares the entry-level zone with the kobold and daggerbeak.
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

Creature.roam_chance     = 30
Creature.respawn_seconds = 180
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Found near graveyards and other resting places of the dead, the ghost presents itself as a pale reflection of what it once was in life.  Its translucent form flickers at the edges, and its eyes — the only truly solid-seeming part of it — fix upon you with cold recognition."

return Creature
