---------------------------------------------------
-- Neartofar Forest — Spawn Registry
-- scripts/zones/neartofar_forest/spawns.lua
---------------------------------------------------
-- Dense deciduous forest west of Wehnimer's Landing.
-- Level range: 10-20
-- Source: gswiki.play.net categories for Neartofar Forest creatures
--
-- Sub-areas:
--   Forest / River paths : Neartofar orc (11), plumed cockatrice (13)
--   Hillside / Ridge     : Neartofar troll (15)
--   Stockade / Barracks  : ogre warrior (20)
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "neartofar_forest"
Spawns.area       = "Neartofar Forest"
Spawns.room_range = { min = 10643, max = 10750 }

Spawns.population = {
    { mob = "neartofar_orc",     level = 11, max = 6, depth = "forest_paths" },
    { mob = "plumed_cockatrice", level = 13, max = 4, depth = "forest_paths" },
    { mob = "neartofar_troll",   level = 15, max = 5, depth = "forest_hillside" },
    { mob = "ogre_warrior",      level = 20, max = 3, depth = "stockade" },
}

return Spawns
