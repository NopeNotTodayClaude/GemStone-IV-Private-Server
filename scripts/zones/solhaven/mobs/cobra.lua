-- Creature: cobra
-- Zone: solhaven / Vornavian Coast  |  Level: 4
-- Source: https://gswiki.play.net/Cobra
-- HP: 51 | AS: 68 (bite) | DS: 37 | bolt: 23 | UDF: 21 | TD: 12
-- ASG: 5N (light leather natural) | Classification: living | Body: ophidian
-- Treasure: no coins, no gems, no magic, no boxes | Skin: a cobra skin
-- Note: Separate file from wehnimers_landing variant (different zone, different ID).
--       Same wiki stats; Vornavian Coast flavor text.
local Creature = {}

Creature.id              = 10123
Creature.name            = "cobra"
Creature.level           = 4
Creature.family          = "reptilian"
Creature.classification  = "living"
Creature.body_type       = "ophidian"

Creature.hp_base         = 51
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 37
Creature.ds_bolt         = 23
Creature.td_spiritual    = 12
Creature.td_elemental    = 12
Creature.udf             = 21
Creature.armor_asg       = 5
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 68, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = {
    "venom",
}

Creature.immune = { "poison" }
Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a cobra skin"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Vornavian Coast — mid-cliffs area, same rooms as mongrel kobold and urgh.
-- Cobras den in the rocky crevices above the waterline.
-- Hard cap; they do not reach the upper cliffs or caverns.
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
Creature.respawn_seconds = 220
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The long, thin, varicolored cobra moves with fluid precision along the coastal rock, its hood spreading wide at your approach.  Salt spray has darkened the leading edge of its scales.  The venom sacs behind its fangs are visibly swollen — a detail worth noting at close range."

return Creature
