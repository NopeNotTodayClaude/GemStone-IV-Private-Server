---------------------------------------------------
-- Fethayl Bog — Spawn Registry
-- scripts/zones/fethayl_bog/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "fethayl_bog"
Spawns.area       = "Fethayl Bog"
Spawns.room_range = { min = 10126, max = 10157 }

-- Population table (informational — actual loading is per-mob .lua file)
Spawns.population = {
    { mob = "bog_wight                     ", level = 44 , max = 4  , depth = "bog_inner" },
    { mob = "bog_spectre                   ", level = 47 , max = 3  , depth = "bog_deep" },
    { mob = "warrior_shade                 ", level = 48 , max = 2  , depth = "bog_deepest" },
}

return Spawns
