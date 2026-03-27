-- Creature: white vysan
-- Zone: icemule_trace / Snowy Forest (Icemule Environs)  |  Level: 3
-- Source: https://gswiki.play.net/White_vysan
-- HP: 50 | AS: 54 (ensnare), 44 (pound) | DS: 4-18 (mid ~11) | ASG: 1N natural
-- TD: minimal (no confirmed values — using 9 per level-3 standard)
-- Treasure: unknown — using animal standard (no coins, skin only)
local Creature = {}

Creature.id              = 10322
Creature.name            = "white vysan"
Creature.level           = 3
Creature.family          = "vysan"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 50
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 11
Creature.ds_bolt         = 8
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "ensnare", as = 54, damage_type = "crush" },
    { type = "pound",   as = 44, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = { "cold" }
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a white vysan pelt"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Icemule Snowy Forest — same entry area as kobold/rolton/rabid squirrel
-- but a step deeper, sharing space with ice skeleton. Keeps cold-theme consistent.
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
Creature.respawn_seconds = 200
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The white vysan stands roughly waist-high on broad, flat feet, its shaggy white coat nearly invisible against the snow.  It has no neck to speak of — the head seems to emerge directly from the torso — and its wide, pawing arms end in thick-fingered hands that grip with surprising force."

return Creature
