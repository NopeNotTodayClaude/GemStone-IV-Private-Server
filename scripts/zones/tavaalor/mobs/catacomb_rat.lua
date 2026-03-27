-- Creature: catacomb rat
-- Zone: tavaalor | Catacombs | Level: 2
-- Source: gswiki.play.net/Catacomb_rat
--
-- A larger, more aggressive cousin of the fanged rodent.  Hairless,
-- pale-skinned from generations underground, with blood-red eyes.
-- Favors the mid-depth tunnels where it nests in refuse and bones.
--
-- GS4 Canon Stats (Level 2):
--   HP: ~30      AS (bite): 30   AS (claw): 26
--   DS: 18       Bolt DS: 12     TD: 6
--   ASG: 1 (thick hairless hide, still no real armor)
--   Experience: ~60 base exp per kill
-- -----------------------------------------------------------------------
local Creature = {}

Creature.id             = 7002
Creature.name           = "catacomb rat"
Creature.level          = 2
Creature.family         = "rodent"
Creature.classification = "living"
Creature.body_type      = "quadruped"

-- ── Vitals ───────────────────────────────────────────────────────────────
Creature.hp_base        = 28
Creature.hp_variance    = 5

-- ── Combat ───────────────────────────────────────────────────────────────
Creature.ds_melee       = 18
Creature.ds_bolt        = 12
Creature.td_spiritual   = 6
Creature.td_elemental   = 6
Creature.udf            = 0
Creature.armor_asg      = 1
Creature.armor_natural  = true

Creature.attacks = {
    { type = "bite",  as = 30, damage_type = "puncture", weight = 55 },
    { type = "claw",  as = 26, damage_type = "slash",    weight = 35 },
    { type = "rake",  as = 24, damage_type = "slash",    weight = 10 }, -- rare rear-leg rake
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Level 2: starts dropping a few coins, still no boxes or gems
Creature.loot_coins   = true     -- small silver drop (1-15 coins)
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a catacomb rat pelt"
Creature.special_loot = {
    "a pale rat tail",           -- ~20% drop, used in minor alchemy
}

-- ── Decay ─────────────────────────────────────────────────────────────────
Creature.decay_seconds = 150
Creature.crumbles      = false
Creature.decay_message = "The catacomb rat's pale body goes limp and begins to decompose."

-- ── Description ──────────────────────────────────────────────────────────
Creature.description = "The catacomb rat is a hairless, pale-skinned creature the size of a small dog.  Generations of living in darkness have bleached its skin to an unhealthy white and turned its eyes a milky crimson.  Its claws are broad and heavily calloused from digging through stone rubble."

-- ── Spawn Rooms ───────────────────────────────────────────────────────────
-- Mid-depth rooms.  Catacomb rats push deeper than fanged rodents.
-- Found from the Sewers inward; rare in the uppermost tunnels.
Creature.spawn_rooms = {
    -- Not yet assigned: zone not built out
}

Creature.roam_rooms = {
    -- Not yet assigned
}

Creature.roam_chance     = 35
Creature.respawn_seconds = 150
Creature.max_count       = 9

return Creature
