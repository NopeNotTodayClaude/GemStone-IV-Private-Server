---------------------------------------------------
-- Ta'Vaalor Catacombs — Spawn Registry
-- scripts/zones/tavaalor/spawns.lua
--
-- Declares all mob populations for the catacombs.
-- The Lua mob loader picks up individual .lua files in mobs/ automatically.
-- This file documents the intended population design and depth tiers for
-- reference, and can be loaded by any zone-management tooling.
--
-- Depth tiers:
--   UPPER  (5909-5922): fanged rodent (primary), catacomb rat (secondary)
--   MID    (5923-5933): catacomb rat (primary), lesser skeleton (primary)
--   DEEP   (5934-5947): skeleton warrior, ghoul, cave worm
--
-- Population summary at full spawn:
--   fanged rodent    12   Level 1   respawn 120s
--   catacomb rat      9   Level 2   respawn 150s
--   lesser skeleton   8   Level 3   respawn 200s
--   skeleton warrior  6   Level 5   respawn 280s
--   ghoul             4   Level 6   respawn 320s
--   cave worm         2   Level 7   respawn 400s
--                   ---
--   Total            41 creatures across 39 rooms
---------------------------------------------------

local Spawns = {}

Spawns.zone      = "tavaalor"
Spawns.area      = "catacombs"
Spawns.room_range = { min = 5909, max = 5947 }

-- Population table (informational — actual loading is per-mob .lua file)
Spawns.population = {
    { mob = "fanged_rodent",    level = 1, max = 12, depth = "upper" },
    { mob = "catacomb_rat",     level = 2, max =  9, depth = "upper_mid" },
    { mob = "lesser_skeleton",  level = 3, max =  8, depth = "mid" },
    { mob = "skeleton_warrior", level = 5, max =  6, depth = "deep" },
    { mob = "ghoul",            level = 6, max =  4, depth = "deep" },
    { mob = "cave_worm",        level = 7, max =  2, depth = "deepest" },
}

return Spawns
