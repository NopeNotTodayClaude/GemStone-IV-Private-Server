-- Creature: lesser skeleton
-- Zone: tavaalor | Catacombs | Level: 3
-- Source: gswiki.play.net/Lesser_skeleton
--
-- Animated bones shambling through the ancient burial chambers.
-- The most basic form of corporeal undead.  Immune to poison and disease.
-- Susceptible to holy attacks, fire, and bludgeoning criticals (bones shatter).
-- Drops coins and occasionally small boxes — early loot for new adventurers.
--
-- GS4 Canon Stats (Level 3):
--   HP: ~40      AS (fist): 38   AS (dagger): 34
--   DS: 28       Bolt DS: 18     TD: 9
--   ASG: 2 (equivalent of light leather, natural bone)
--   Experience: ~90 base exp per kill
--   Undead: immune to poison/disease, resist cold
-- -----------------------------------------------------------------------
local Creature = {}

Creature.id             = 7003
Creature.name           = "lesser skeleton"
Creature.level          = 3
Creature.family         = "skeleton"
Creature.classification = "corporeal_undead"
Creature.body_type      = "biped"

-- ── Vitals ───────────────────────────────────────────────────────────────
Creature.hp_base        = 38
Creature.hp_variance    = 6

-- ── Combat ───────────────────────────────────────────────────────────────
-- Armed with a makeshift dagger (scavenged from burial goods).
-- Prefers the closed-fist smash when disarmed.
Creature.ds_melee       = 28
Creature.ds_bolt        = 18
Creature.td_spiritual   = 9
Creature.td_elemental   = 9
Creature.udf            = 0
Creature.armor_asg      = 2      -- ASG 2: natural bone is roughly light leather equivalent
Creature.armor_natural  = true

Creature.attacks = {
    { type = "closed_fist", as = 38, damage_type = "crush",    weight = 45 },
    { type = "dagger",      as = 34, damage_type = "puncture", weight = 55 },
}

Creature.spells    = {}
Creature.abilities = {}

-- Undead immunities and resistances (GS4 canonical)
Creature.immune = { "poison", "disease" }
Creature.resist = { "cold" }

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Level 3 undead: drops coins, small chance for a box.
-- Skin is the knuckle joint — used in minor necromantic recipes.
Creature.loot_coins   = true     -- 5-40 silver coins
Creature.loot_gems    = true     -- ~10% gem drop (low-value: clear zircon, etc.)
Creature.loot_magic   = false
Creature.loot_boxes   = true     -- ~15% small locked box
Creature.skin         = "a skeleton knuckle"
Creature.special_loot = {}

-- ── Decay ─────────────────────────────────────────────────────────────────
Creature.decay_seconds = 200
Creature.crumbles      = true    -- GS4 canon: skeletons crumble to dust
Creature.decay_message = "The lesser skeleton collapses into a heap of crumbling bones and dust."

-- ── Description ──────────────────────────────────────────────────────────
Creature.description = "The lesser skeleton is an animated framework of yellowed bones, loosely held together by dark, dried sinew.  A few scraps of burial clothing cling to its frame.  Its empty eye sockets hold a faint phosphorescent gleam that dims when it is destroyed."

-- ── Spawn Rooms ───────────────────────────────────────────────────────────
-- Mid-depth rooms.  Skeletons begin appearing around the Sewers and
-- Passageways, deeper than the rodents.  Found wherever old bones are
-- numerous: torture chambers, altar areas, burial passages.
Creature.spawn_rooms = {
    -- Not yet assigned: zone not built out
}

Creature.roam_rooms = {
    -- Not yet assigned
}

Creature.roam_chance     = 20    -- undead move deliberately, less wandering
Creature.respawn_seconds = 200
Creature.max_count       = 8

return Creature
