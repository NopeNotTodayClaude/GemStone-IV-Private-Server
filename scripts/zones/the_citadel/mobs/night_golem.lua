-- Creature: night golem
-- Zone: the_citadel / River Tunnels  |  Level: 5
-- Source: https://gswiki.play.net/Night_golem
-- HP: 65 | AS: 96 (ensnare), 86 (pound) | DS: 11-72 (mid ~42) | bolt: 5
-- UDF: 77-117 (mid ~97) | ASG: 12N (brigandine natural) | TD: 15 (elemental)
-- Treasure: coins yes, gems yes, magic yes, boxes yes | Skin: a night golem finger
local Creature = {}

Creature.id              = 10414
Creature.name            = "night golem"
Creature.level           = 5
Creature.family          = "golem"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 65
Creature.hp_variance     = 6

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: ensnare 96 AS, pound 86 AS, DS 11-72 (mid 42), bolt 5, UDF 77-117 (mid 97)
-- TD 15 elemental/Major Elemental only — no spiritual TD listed
Creature.ds_melee        = 42
Creature.ds_bolt         = 5
Creature.td_spiritual    = 0
Creature.td_elemental    = 15
Creature.udf             = 97
Creature.armor_asg       = 12
Creature.armor_natural   = true

Creature.attacks = {
    { type = "ensnare", as = 96, damage_type = "crush" },
    { type = "pound",   as = 86, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = {
    "golem_reconstruct",     -- partially rebuilds after taking damage
}

Creature.immune = {
    "disease",
    "poison",
    "fear",
}
Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a night golem finger"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- The Citadel River Tunnels — the entry portion of the citadel complex.
-- Hard cap to citadel rooms; golems are bound to the tunnels they were
-- created to guard and do not wander outside.
Creature.spawn_rooms = {
    11063, 11064, 11065, 11066,
    11123, 11124, 11125, 11126,
    11127, 11128, 11129, 11130,
    11131, 11132, 11133, 11134,
    11135, 11136, 11137, 11138,
    11139, 11140, 11141, 11142,
    11143, 11144, 11145, 11146,
    11147, 11148, 11149, 11150,
}

Creature.roam_rooms = {
    11063, 11064, 11065, 11066,
    11123, 11124, 11125, 11126,
    11127, 11128, 11129, 11130,
    11131, 11132, 11133, 11134,
    11135, 11136, 11137, 11138,
    11139, 11140, 11141, 11142,
    11143, 11144, 11145, 11146,
    11147, 11148, 11149, 11150,
}

Creature.roam_chance     = 15
Creature.respawn_seconds = 240
Creature.max_count       = 6

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Formed by the alchemists of the Citadel in their service to the Council of Twelve, these 4-foot tall golems appear to be sculpted of pure shadow.  Approximately man-shaped but with proportions subtly wrong, they move without sound and radiate a cold that has nothing to do with temperature.  Their construction means that lesser injuries simply close and are forgotten — only sustained damage finally brings them down."

return Creature
