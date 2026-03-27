-- Creature: greater ice spider
-- Zone: icemule_trace / Glatoph lower (Snowflake Vale equivalent)  |  Level: 3
-- Source: https://gswiki.play.net/Greater_ice_spider
-- HP: 44 | AS: 71 (stinger), 48 (pincer) | DS: 29-81 (mid ~55) | bolt: 35
-- ASG: 1N natural | TD: 9 | ability: web (immobilize)
-- Treasure: no coins (arachnid) | Skin: spider leg
local Creature = {}

Creature.id              = 10321
Creature.name            = "greater ice spider"
Creature.level           = 3
Creature.family          = "arachnid"
Creature.classification  = "living"
Creature.body_type       = "arachnid"

Creature.hp_base         = 44
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: stinger 71 AS, pincer 48 AS, DS 29-81 mid, bolt 35, ASG 1N
Creature.ds_melee        = 55
Creature.ds_bolt         = 35
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "sting",  as = 71, damage_type = "puncture" },
    { type = "pincer", as = 48, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = {
    "venom",
    "web_immobilize",
}
Creature.immune = { "cold", "poison" }
Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a spider leg"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Glatoph lower rooms — same block as ice skeleton (2558-4122 range).
-- Snowflake Vale is the canonical area; these rooms are the nearest
-- equivalent in the built zone. Hard cap prevents reaching mid-glatoph.
Creature.spawn_rooms = {
    2558, 2559, 2560, 2561,
    2562, 2563, 2564, 2565,
    3678, 3679, 3680, 3681,
    3682, 4122,
}

Creature.roam_rooms = {
    2558, 2559, 2560, 2561,
    2562, 2563, 2564, 2565,
    3678, 3679, 3680, 3681,
    3682, 4122,
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 200
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The greater ice spider's body is a translucent blue-white, and the ice crystals that form along its legs give it an almost beautiful appearance at a distance.  Closer inspection reveals the stinger coiled beneath its abdomen and the webs it trails — not silk, but frozen filament strong enough to pin a limb."

return Creature
