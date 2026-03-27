---------------------------------------------------
-- Yander's Farm — Spawn Registry
-- scripts/zones/yanders_farm/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "yanders_farm"
Spawns.area       = "Yander's Farm"
Spawns.room_range = { min = 6012, max = 10486 }

-- Population table (informational — actual loading is per-mob .lua file)
Spawns.population = {
    { mob = "great_boar                    ", level = 10 , max = 5  , depth = "wheat_fields" },
    { mob = "giant_marmot                  ", level = 10 , max = 6  , depth = "wheat_barley" },
    { mob = "raider_orc                    ", level = 10 , max = 6  , depth = "wheat_barley" },
    { mob = "dark_orc                      ", level = 12 , max = 5  , depth = "corn_fields" },
    { mob = "great_stag                    ", level = 13 , max = 4  , depth = "corn_barley" },
    { mob = "grey_orc                      ", level = 14 , max = 5  , depth = "corn_barley_deep" },
}

return Spawns
