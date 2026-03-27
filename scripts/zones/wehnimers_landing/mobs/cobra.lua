-- Creature: cobra
-- Zone: wehnimers_landing / The Graveyard  |  Level: 4
-- Source: https://gswiki.play.net/Cobra
-- HP: 51 | AS: 68 (bite) | DS: 37 | bolt: 23 | UDF: 21 | TD: 12
-- ASG: 5N (light leather natural) | Classification: living | Body: ophidian
-- Treasure: no coins, no gems, no magic, no boxes | Skin: a cobra skin
-- Note: wiki lists Graveyard + Vornavian Coast. This file covers the Graveyard.
--       See solhaven/mobs/cobra.lua for the Vornavian Coast variant (separate ID).
local Creature = {}

Creature.id              = 9328
Creature.name            = "cobra"
Creature.level           = 4
Creature.family          = "reptilian"
Creature.classification  = "living"
Creature.body_type       = "ophidian"

Creature.hp_base         = 51
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: bite 68 AS, DS 37, bolt 23, UDF 21, TD 12
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
-- The Graveyard — cobras lurk among the headstones at a step above the
-- level 2 lesser shades and phantoms. Hard boundary to graveyard rooms.
Creature.spawn_rooms = {
    7163, 7164, 7165, 7166, 7167,
    7168, 7169, 7170, 7171, 7172,
    7173, 7174, 7175, 7176, 7177,
    7178, 7179, 7180, 7181, 7182,
    7183, 7184, 7185, 7186, 7187,
    7188, 7189, 7190, 7191, 7192,
    7193, 7194, 7195, 7196, 7197,
    7198, 7199, 7200, 7201, 7202,
    7203, 7204, 7205, 7206, 7207,
    7208, 7209, 7210, 7211, 7212,
    7213, 7214, 7245, 7246, 7247,
    7248, 7249, 7250, 7251, 7252,
    7253, 7254,
}

Creature.roam_rooms = {
    7163, 7164, 7165, 7166, 7167,
    7168, 7169, 7170, 7171, 7172,
    7173, 7174, 7175, 7176, 7177,
    7178, 7179, 7180, 7181, 7182,
    7183, 7184, 7185, 7186, 7187,
    7188, 7189, 7190, 7191, 7192,
    7193, 7194, 7195, 7196, 7197,
    7198, 7199, 7200, 7201, 7202,
    7203, 7204, 7205, 7206, 7207,
    7208, 7209, 7210, 7211, 7212,
    7213, 7214, 7245, 7246, 7247,
    7248, 7249, 7250, 7251, 7252,
    7253, 7254,
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 220
Creature.max_count       = 9

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The long, thin, varicolored cobra slithers quickly through the graveyard, its hood spreading wide as it senses a target nearby.  Its scales catch what little light reaches this place and throw back a brief, cold glitter.  The venom sacs behind its fangs are visibly swollen."

return Creature
