-- Creature: carrion worm
-- Zone: icemule_trace / Snowy Forest (Icemule Environs)  |  Level: 1
-- Source: https://gswiki.play.net/Carrion_worm
-- HP: 28 | AS: 39 (charge), 29 (bite) | DS: 27-68 | bolt DS: 25 | TD: 3
-- UDF: 40 | ASG: 1N (natural) | Treasure: none. Skin: worm skin
-- Separate file from solhaven variant — different zone, different ID,
-- same creature stats per wiki. Snow-adapted flavor text.
local Creature = {}

Creature.id              = 10318
Creature.name            = "carrion worm"
Creature.level           = 1
Creature.family          = "worm"
Creature.classification  = "living"
Creature.body_type       = "worm"

Creature.hp_base         = 28
Creature.hp_variance     = 4

-- ── Combat ────────────────────────────────────────────────────────────────
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
-- Icemule Snowy Forest entry area — same rooms as rolton and kobold_imt.
-- Roam boundary hard-capped to snowy forest; will not drift into glatoph.
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

Creature.roam_chance     = 20
Creature.respawn_seconds = 150
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The carrion worm burrows through the frozen soil of the snowy forest, erupting where the scent of blood reaches it.  Its pale, slimy body tapers to a point at the tail end, and at the business end rows of short, sharp teeth gnash continuously.  Cold has done nothing to blunt its appetite."

return Creature
