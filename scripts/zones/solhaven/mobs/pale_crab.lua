-- Creature: pale crab
-- Zone: solhaven / Solhaven Environs (Coastal Cliffs)  |  Level: 2
-- Source: https://gswiki.play.net/Pale_crab
-- HP: 36 | AS: 43 (claw + ensnare) | DS: 27 melee / 24 bolt | TD: 6
-- ASG: 1N (natural) | Classification: living | Body: crustacean
-- Treasure: coins yes, gems yes, magic yes, boxes yes | Skin: a pale crab claw
local Creature = {}

Creature.id              = 10119
Creature.name            = "pale crab"
Creature.level           = 2
Creature.family          = "crab"
Creature.classification  = "living"
Creature.body_type       = "crustacean"

Creature.hp_base         = 36
Creature.hp_variance     = 4

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: claw 43 AS, ensnare 43 AS, DS 27, ranged 49, bolt 24, TD 6
Creature.ds_melee        = 27
Creature.ds_bolt         = 24
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "claw",    as = 43, damage_type = "slash" },
    { type = "ensnare", as = 43, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: coins yes, gems yes, magic yes, boxes yes. Skin: pale crab claw (inferred).
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a pale crab pincer"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Coastal Cliffs lower area (Solhaven Environs). Crabs occupy the same
-- shoreline rooms as the level-1 pack, scuttling among the tide pools.
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
Creature.description = "Bleached to a sickly off-white by years among the tide pools, the pale crab is not particularly large but compensates with powerful, asymmetrical claws.  The larger of the two is capable of pinning a limb entirely, while the smaller delivers a sawing slash.  It moves sideways with unsettling speed."

return Creature
