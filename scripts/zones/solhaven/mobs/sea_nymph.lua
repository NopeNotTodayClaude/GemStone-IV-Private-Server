-- Creature: sea nymph
-- Zone: solhaven / Solhaven Environs (Coastal Cliffs)  |  Level: 2
-- Source: https://gswiki.play.net/Sea_nymph
-- HP: 44 | AS: 50 (dagger/handaxe/spear) | CS: 10 (Calm 201), 2 (Vibration 1002)
-- DS: 10-56 (mid ~33) | bolt DS: 7 | UDF: 52 | TD: 6 | ASG: 2 (robes)
-- Treasure: coins yes, gems yes, magic yes, boxes yes | Skin: a sea nymph lock
local Creature = {}

Creature.id              = 10120
Creature.name            = "sea nymph"
Creature.level           = 2
Creature.family          = "fey"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 44
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: dagger/handaxe/spear all 50 AS, CS 10 (Calm), 2 (Vibration Chant)
-- DS 10-56 (using midpoint 33), bolt 7, UDF 52, TD 6 all schools
Creature.ds_melee        = 33
Creature.ds_bolt         = 7
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 52
Creature.armor_asg       = 2
Creature.armor_natural   = false

Creature.attacks = {
    { type = "dagger",  as = 50, damage_type = "puncture" },
    { type = "handaxe", as = 50, damage_type = "slash" },
    { type = "spear",   as = 50, damage_type = "puncture" },
}

Creature.spells = {
    { name = "Calm (201)",             cs = 10, as = 0 },
    { name = "Vibration Chant (1002)", cs = 2,  as = 0 },
}

Creature.abilities = {
    "glamour",
}

Creature.immune = {}
Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: coins yes, gems yes, magic yes, boxes yes. Skin inferred from creature type.
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a sea nymph lock"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Coastal Cliffs lower area (Solhaven Environs). Nymphs dwell among the rocks
-- and tide pools at the cliff base alongside pale crabs and ghosts.
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

Creature.roam_chance     = 25
Creature.respawn_seconds = 180
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The sea nymph's voice carries clearly over the sound of the surf, and there is something in it that makes the listener want to stop and listen further.  Her pale blue-green skin and salt-tangled hair give her the look of something that crawled out of the ocean and elected to stay, and her weapons — carried casually, used with absolute competence — suggest she was never helpless."

return Creature
