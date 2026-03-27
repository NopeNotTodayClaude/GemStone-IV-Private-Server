-- Creature: carrion worm
-- Zone: solhaven / Solhaven Environs (Coastal Cliffs)  |  Level: 1
-- Source: https://gswiki.play.net/Carrion_worm
-- HP: 28 | AS: 39 (charge), 29 (bite) | DS: 27-68 | bolt DS: 25 | TD: 3
-- UDF: 40 | ASG: 1N (natural) | Treasure: none. Skin: worm skin
local Creature = {}

Creature.id              = 10117
Creature.name            = "carrion worm"
Creature.level           = 1
Creature.family          = "worm"
Creature.classification  = "living"
Creature.body_type       = "worm"

Creature.hp_base         = 28
Creature.hp_variance     = 4

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: charge 39 AS, bite 29 AS, DS 27-68, bolt 25, UDF 40, TD 3
-- Using DS midpoint 47. Charge is primary, bite secondary.
Creature.ds_melee        = 47
Creature.ds_bolt         = 25
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 40
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "charge", as = 39, damage_type = "crush" },
    { type = "bite",   as = 29, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: no coins, no gems, no magic, no boxes. Skin: worm skin.
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a worm skin"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Coastal Cliffs lower area (Solhaven Environs). Carrion worms inhabit the
-- same entry-level cliffs as kobolds — scavenging cliff-face carrion.
-- Roam boundary is hard-capped here; they do NOT reach the upper cliffs.
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

Creature.roam_chance     = 20
Creature.respawn_seconds = 150
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The carrion worm eagerly consumes anything dead and anything living that doesn't put up too much of a fight.  Its long, slimy body tapers to a point at the tail end.  At the business end, several hundred waving cilia force food into the worm's maw where the food is crushed by rows of short, sharp teeth.  The carrion worm hunts blindly, using its keen sense of smell and hearing to locate its prey."

return Creature
