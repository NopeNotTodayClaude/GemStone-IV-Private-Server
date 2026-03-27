---------------------------------------------------
-- Grasslands & Foothills — Spawn Registry
-- scripts/zones/grasslands/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "grasslands"
Spawns.area       = "Grasslands & Foothills"
Spawns.room_range = { min = 10171, max = 10267 }

-- Population table (informational — actual loading is per-mob .lua file)
Spawns.population = {
    { mob = "agresh_troll_scout            ", level = 14 , max = 5  , depth = "barley_field" },
    { mob = "black_leopard                 ", level = 15 , max = 5  , depth = "foothills_orchard" },
    { mob = "agresh_bear                   ", level = 16 , max = 4  , depth = "apple_orchard" },
    { mob = "agresh_troll_warrior          ", level = 16 , max = 5  , depth = "vineyard" },
    { mob = "plains_ogre                   ", level = 17 , max = 4  , depth = "foothills_grassland" },
    { mob = "plains_lion                   ", level = 18 , max = 5  , depth = "foothills_grassland" },
    { mob = "agresh_troll_chieftain        ", level = 20 , max = 2  , depth = "foothills_deep" },
}

return Spawns
