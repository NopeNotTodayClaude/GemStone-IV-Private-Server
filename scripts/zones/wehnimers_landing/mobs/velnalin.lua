-- Creature: velnalin
-- Zone: wehnimers_landing / Wehnimer's Environs (Trollfang entry)  |  Level: 3
-- Source: https://gswiki.play.net/Velnalin
-- HP: 44 | AS: 71 (charge), 61 (bite/stomp) | DS: 32 | bolt: 13 | ASG: 1N natural
-- TD: 9 | Treasure: none | Skin: velnalin pelt
local Creature = {}

Creature.id              = 9326
Creature.name            = "velnalin"
Creature.level           = 3
Creature.family          = "deer"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 44
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 32
Creature.ds_bolt         = 13
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "charge", as = 71, damage_type = "crush" },
    { type = "bite",   as = 61, damage_type = "puncture" },
    { type = "stomp",  as = 61, damage_type = "crush" },
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
Creature.skin         = "a velnalin hide"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Open trollfang scrub alongside gaks and snowcats. Hard boundary keeps
-- them at the entry level; they do not reach the deeper trollfang zones.
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

Creature.roam_chance     = 35
Creature.respawn_seconds = 180
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The velnalin resembles a large, athletic deer — until it opens its mouth and reveals a set of sharp, interlocking teeth completely inappropriate for an herbivore.  It watches you with calm, dark eyes, then charges without warning at a speed its build should not permit."

return Creature
