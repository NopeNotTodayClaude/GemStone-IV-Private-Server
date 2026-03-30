---------------------------------------------------
-- Ta'Vaalor Catacombs — Spawn Registry
-- scripts/zones/tavaalor/spawns.lua
--
-- Local map source of truth:
--   map_files/EN-tavaalor-1534463105.png
--   map_files/en-tavaalor-1565907614.png
--
-- The catacombs shown on the Ta'Vaalor map are labeled only:
--   Fanged Rodent (1)
--
-- So for the mapped city catacombs, fanged rodents are the only valid
-- hunting population.  Any deeper catacomb population must not spawn here
-- unless/until a separate local map is added that explicitly places it.
---------------------------------------------------

local Spawns = {}

Spawns.zone      = "tavaalor"
Spawns.area      = "catacombs"
Spawns.map_locked = true
Spawns.room_range = { min = 5909, max = 5947 }

Spawns.population = {
    { mob = "fanged_rodent", level = 1, max = 12, depth = "catacombs" },
}





Spawns.mob_rooms = {
    fanged_rodent = {
        5909, 5910, 5911, 5912, 5913, 5914, 5915, 5916, 5917, 5918,
        5919, 5920, 5921, 5922, 5923, 5925, 5926, 5927, 5928, 5929,
        5932, 5933, 5936, 5939, 5943, 5945, 5946, 5947
    },
}

return Spawns
