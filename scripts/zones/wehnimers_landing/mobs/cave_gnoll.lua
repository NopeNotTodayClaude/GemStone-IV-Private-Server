-- Creature: cave gnoll
-- Zone: wehnimers_landing / Wehnimer's Environs (Trollfang entry)  |  Level: 3
-- Source: https://gswiki.play.net/Cave_gnoll
-- HP: 60 | AS: 68 (scimitar) | DS: 28 | bolt DS: 9 | TD: 9 | ASG: 7 (reinforced leather)
-- Treasure: coins yes, gems yes, boxes yes | Skin: cave gnoll hide
local Creature = {}

Creature.id              = 9323
Creature.name            = "cave gnoll"
Creature.level           = 3
Creature.family          = "gnoll"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 60
Creature.hp_variance     = 6

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 28
Creature.ds_bolt         = 9
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 0
Creature.armor_asg       = 7
Creature.armor_natural   = false

Creature.attacks = {
    { type = "scimitar", as = 68, damage_type = "slash" },
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
Creature.skin         = "a cave gnoll hide"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Trollfang entry area — shares the scrub with goblin and hobgoblin.
-- Hard boundary prevents bleeding into level 5+ zones.
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

Creature.roam_chance     = 25
Creature.respawn_seconds = 200
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Hyena-headed and hump-backed, the cave gnoll has adapted to dim tunnels and cramped spaces without losing any of its aggression.  Its pale, watery eyes catch available light and its scimitar — too large for the cramped spaces it apparently prefers — it swings with practiced efficiency anyway."

return Creature
