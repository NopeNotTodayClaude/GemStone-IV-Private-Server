-- Creature: Bresnahanini rolton
-- Zone: the_outlands / Vornavis Outlands  |  Level: 3
-- Source: https://gswiki.play.net/Bresnahanini_rolton
-- HP: 44 | AS: 70 (charge), 60 (bite) | DS: 44 | bolt: 17 | UDF: 75 | TD: 9
-- ASG: 5N (light leather natural) | Classification: living | Body: quadruped
-- Treasure: no coins, no gems, no boxes | Skin: a rolton eye
local Creature = {}

Creature.id              = 10412
Creature.name            = "Bresnahanini rolton"
Creature.level           = 3
Creature.family          = "caprine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 44
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: charge 70 AS, bite 60 AS, DS 44, bolt 17, UDF 75, TD ~9, ASG 5N
Creature.ds_melee        = 44
Creature.ds_bolt         = 17
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 75
Creature.armor_asg       = 5
Creature.armor_natural   = true

Creature.attacks = {
    { type = "charge", as = 70, damage_type = "crush" },
    { type = "bite",   as = 60, damage_type = "puncture" },
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
Creature.skin         = "a rolton eye"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Vornavis Outlands open plains (zone 94). The entry portion of the zone
-- (rooms 5465-5530) is the flat pasture. Hard cap prevents roaming to
-- the deeper outlands roads.
Creature.spawn_rooms = {
    5465, 5466, 5467, 5468, 5469,
    5470, 5471, 5472, 5473, 5474,
    5475, 5476, 5477, 5478, 5479,
    5480, 5481, 5482, 5483, 5484,
    5485, 5486, 5487, 5488, 5489,
    5490, 5491, 5492, 5493, 5494,
}

Creature.roam_rooms = {
    5465, 5466, 5467, 5468, 5469,
    5470, 5471, 5472, 5473, 5474,
    5475, 5476, 5477, 5478, 5479,
    5480, 5481, 5482, 5483, 5484,
    5485, 5486, 5487, 5488, 5489,
    5490, 5491, 5492, 5493, 5494,
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 180
Creature.max_count       = 10

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The Bresnahanini rolton is a prime example of the breed favoured by the Vornavian farmsteads — which is to say, it is filthy, aggressive, and in possession of incisors that would look more appropriate on something predatory.  Its matted grey-white pelt smells powerfully of wet wool and worse, and its hooves are cracked and stained with the earth of the Outlands.  It watches you with the flat, hostile gaze of something that has never in its life backed down from a confrontation."

return Creature
