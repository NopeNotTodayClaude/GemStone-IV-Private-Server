-- Creature: mountain snowcat
-- Zone: wehnimers_landing / Wehnimer's Environs (Trollfang entry)  |  Level: 3
-- Source: https://gswiki.play.net/Mountain_snowcat
-- HP: 44 | AS: 59 (bite/claw) | DS: 26 | bolt: 34 | ASG: 1N natural
-- TD: 9 | Treasure: no coins, no boxes | Skin: snowcat pelt
local Creature = {}

Creature.id              = 9327
Creature.name            = "mountain snowcat"
Creature.level           = 3
Creature.family          = "feline"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 44
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 26
Creature.ds_bolt         = 34
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 59, damage_type = "puncture" },
    { type = "claw", as = 59, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = { "pounce" }
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a snowcat pelt"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Trollfang entry scrub — hunts the same area as velnalin and gaks.
-- Hard boundary; snowcats stay at the entry level.
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
Creature.respawn_seconds = 200
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Compact and powerful beneath a thick cream-and-grey coat, the mountain snowcat moves through the scrub in almost total silence.  Its paws are oversized for its body — natural snowshoes — and its eyes are pale gold, patient, and entirely predatory.  You probably will not see it until it has already decided to move."

return Creature
