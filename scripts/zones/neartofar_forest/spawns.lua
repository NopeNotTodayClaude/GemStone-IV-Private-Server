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
Spawns.room_range = { min = 10622, max = 10750 }
Spawns.map_locked = true

Spawns.population = {
    { mob = "neartofar_orc",     level = 11, max = 6, depth = "forest_paths" },
    { mob = "plumed_cockatrice", level = 13, max = 4, depth = "forest_paths" },
    { mob = "neartofar_troll",   level = 15, max = 5, depth = "forest_hillside" },
    { mob = "ogre_warrior",      level = 20, max = 3, depth = "stockade" },
}






Spawns.mob_rooms = {
    plumed_cockatrice = {
        10622, 10623, 10624, 10625, 10626, 10627, 10628, 10629, 10630, 10631,
        10632, 10633, 10634, 10635, 10636, 10637, 10638, 10639, 10640, 10641,
        10642
    },
    neartofar_orc = {
        10643, 10644, 10650, 10651, 10652, 10653, 10654, 10655, 10656, 10657,
        10647, 10648, 10649, 10658, 10659
    },
    neartofar_troll = {
        10643, 10644, 10650, 10651, 10652, 10653, 10656, 10657
    },
    ogre_warrior = {
        10660, 10661, 10662, 10663, 10664, 10665, 10666, 10667, 10643, 10644
    },
}

return Spawns
