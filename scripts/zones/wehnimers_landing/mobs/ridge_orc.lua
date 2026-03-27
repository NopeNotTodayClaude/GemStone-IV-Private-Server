-- Creature: ridge orc
-- Zone: wehnimers_landing / Dead Plateau (Upper Trollfang mid)  |  Level: 4
-- Source: https://gswiki.play.net/Ridge_orc
-- HP: 80 | AS: 84 (handaxe) | DS: 78 | bolt: 23 | UDF: 103 | TD: 12
-- ASG: 5 (light leather) | Classification: living | Body: biped
-- Treasure: coins yes, gems yes, magic yes, boxes yes | Skin: an orc ear
local Creature = {}

Creature.id              = 9329
Creature.name            = "ridge orc"
Creature.level           = 4
Creature.family          = "orc"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 80
Creature.hp_variance     = 7

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: handaxe 84 AS, DS 78, bolt 23, UDF 103, TD 12
Creature.ds_melee        = 78
Creature.ds_bolt         = 23
Creature.td_spiritual    = 12
Creature.td_elemental    = 12
Creature.udf             = 103
Creature.armor_asg       = 5
Creature.armor_natural   = false

Creature.attacks = {
    { type = "handaxe", as = 84, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "an orc ear"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Dead Plateau / Upper Trollfang — sits between the level 2-3 entry pack
-- and the level 5-6 deeper trollfang orcs. Hard boundary prevents bleeding
-- into the level 6 lesser orc zones (rooms 1196+).
Creature.spawn_rooms = {
    452, 453, 454, 455,
    456, 457, 458, 459,
    460, 461, 462, 463,
    464, 465, 466, 467,
    468, 469, 470, 471,
    472, 473, 474, 475,
}

Creature.roam_rooms = {
    452, 453, 454, 455,
    456, 457, 458, 459,
    460, 461, 462, 463,
    464, 465, 466, 467,
    468, 469, 470, 471,
    472, 473, 474, 475,
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 220
Creature.max_count       = 3

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Massive and sullen looking, the ridge orc glares and grimaces at all who dare to approach.  It stands half a head taller than most orcs and its shoulders are so broad they seem architectural.  The handaxe it carries is barely a handaxe by size — the grip alone is as wide as a forearm."

return Creature
