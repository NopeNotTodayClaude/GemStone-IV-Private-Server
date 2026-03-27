-- Creature: cave worm
-- Zone: tavaalor | Catacombs Deep | Level: 7
-- Source: gswiki.play.net/Cave_worm
--
-- Enormous blind worms that have tunneled through the lowest levels over
-- centuries.  They sense prey through vibration and heat.  Their thick
-- segmented hide makes them highly resistant to slashing and somewhat
-- resistant to puncture.  Crushing attacks are most effective.
--
-- Special ability: constrict_maneuver — the worm ensnares a target and
-- begins crushing.  On success, target is held (prone equivalent) and
-- takes crush damage each round until they break free or the worm is
-- killed.  This is a standard GS4 worm/constrictor mechanic.
--
-- GS4 Canon Stats (Level 7):
--   HP: ~90      AS (ensnare): 92   AS (bite): 86
--   DS: 76       Bolt DS: 50        TD: 21
--   ASG: 6 (heavy leather equivalent — thick segmented hide)
--   Experience: ~220 base exp per kill
--   Resist cold; gems in loot (swallowed treasure from past victims)
-- -----------------------------------------------------------------------
local Creature = {}

Creature.id             = 7006
Creature.name           = "cave worm"
Creature.level          = 7
Creature.family         = "worm"
Creature.classification = "living"
Creature.body_type      = "ophidian"   -- no limb criticals; crush crits dominant

-- Vitals
Creature.hp_base        = 88
Creature.hp_variance    = 12

-- Combat
-- Ensnare is the primary opener; bite follows once prey is held.
Creature.ds_melee       = 76
Creature.ds_bolt        = 50
Creature.td_spiritual   = 21
Creature.td_elemental   = 21
Creature.udf            = 0
Creature.armor_asg      = 6      -- ASG 6: heavy leather equiv, thick segments
Creature.armor_natural  = true

Creature.attacks = {
    { type = "ensnare", as = 92, damage_type = "crush",    weight = 45 },
    { type = "bite",    as = 86, damage_type = "puncture", weight = 40 },
    { type = "slam",    as = 80, damage_type = "crush",    weight = 15 },
}

Creature.spells    = {}
Creature.abilities = { "constrict_maneuver" }
Creature.immune    = {}
Creature.resist    = { "cold" }   -- cold-blooded, less affected by cold

-- Loot
-- No coins (no pockets) but drops gems — swallowed from past victims.
-- Worm fang is a crafting component (tough and hollow, used in tools).
Creature.loot_coins   = false
Creature.loot_gems    = true     -- ~40% gem (swallowed from digested prey)
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a worm skin"
Creature.special_loot = {
    "a worm fang",               -- ~35% drop, crafting component
    "a worm gland",              -- ~15% drop, alchemical use
}

-- Decay
Creature.decay_seconds = 360
Creature.crumbles      = false
Creature.decay_message = "The cave worm's segmented body goes limp, its crushing coils finally still."

-- Description
Creature.description = "The cave worm is a massive, eyeless creature nearly twenty feet in length.  Its pale, segmented body is covered in overlapping chitinous plates thick enough to turn aside most blades.  A ring of sensory pits around its blunt head allows it to track prey by heat and vibration alone.  Its maw is lined with rows of backwards-curved fangs designed to prevent escape."

-- Spawn Rooms — restricted to the absolute lowest rooms
-- Serpent's Den (5934), Lair (5935), and the deep Pool (5944) only.
-- These worms are rare and territorial; only two or three exist at a time.
Creature.spawn_rooms = {
    -- Not yet assigned: zone not built out
}

Creature.roam_rooms = {
    -- Not yet assigned
}

Creature.roam_chance     = 10    -- slow-moving, nearly sessile between feeds
Creature.respawn_seconds = 400
Creature.max_count       = 2     -- territorial — only 2 at a time in the zone

return Creature
