-- Creature: striped gak
-- Zone: wehnimers_landing / Wehnimer's Environs (Trollfang entry)  |  Level: 3
-- Source: https://gswiki.play.net/Striped_gak
-- HP: 80 | AS: 61 (impale/charge) | DS: 40 | bolt: 12 | UDF: 73 | TD: 9
-- ASG: 6N (full leather natural) | Treasure: none | Skin: a gak hide
local Creature = {}

Creature.id              = 9324
Creature.name            = "striped gak"
Creature.level           = 3
Creature.family          = "bovine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 80
Creature.hp_variance     = 7

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 40
Creature.ds_bolt         = 12
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 73
Creature.armor_asg       = 6
Creature.armor_natural   = true

Creature.attacks = {
    { type = "charge", as = 61, damage_type = "crush" },
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
Creature.skin         = "a gak pelt"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Trollfang entry open terrain — same block as spotted gak (level 2).
-- Striped gak pushes slightly deeper into the scrub.
Creature.spawn_rooms = {
    452, 453, 454, 455,
    456, 457, 458, 459,
    460, 461, 462, 463,
    464, 465, 466, 467,
}

Creature.roam_rooms = {
    452, 453, 454, 455,
    456, 457, 458, 459,
    460, 461, 462, 463,
    464, 465, 466, 467,
    468, 469, 470, 471,
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 180
Creature.max_count       = 3

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Where the spotted gak is merely large and hostile, the striped gak seems to have channeled its additional age into additional meanness.  Bold dark stripes cut across its heavy brown pelt and its horns are longer and more curved than its spotted kin.  It paws the earth, lowers its head, and commits."

return Creature
