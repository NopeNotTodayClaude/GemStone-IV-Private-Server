---------------------------------------------------
-- Teras Isle / Fhorian Village — Spawn Registry
-- scripts/zones/teras_isle/spawns.lua
---------------------------------------------------
local Spawns = {}
Spawns.zone       = "teras_isle"
Spawns.area       = "Teras Isle / Fhorian Village"
Spawns.room_range = { min = 1998, max = 12767 }
Spawns.population = {
    { mob = "jungle_troll                       ", level = 26 , max = 4  , depth = "greymist_wood" },
    { mob = "giant_fog_beetle                   ", level = 32 , max = 3  , depth = "greymist_wood" },
    { mob = "jungle_troll_chieftain             ", level = 30 , max = 2  , depth = "greymist_wood_deep" },
    { mob = "banshee                            ", level = 50 , max = 2  , depth = "mausoleum_catacombs" },
    { mob = "scaly_burgee                       ", level = 29 , max = 4  , depth = "basalt_flats_beach" },
    { mob = "fire_ogre                          ", level = 28 , max = 4  , depth = "basalt_flats" },
    { mob = "ash_hag                            ", level = 31 , max = 3  , depth = "volcanic_slope" },
    { mob = "lava_troll                         ", level = 34 , max = 4  , depth = "geyser_flats" },
    { mob = "fire_giant                         ", level = 36 , max = 3  , depth = "geyser_flats_deep" },
    { mob = "siren_lizard                       ", level = 42 , max = 4  , depth = "eye_of_vtull_lava" },
    { mob = "firethorn_shoot                    ", level = 44 , max = 4  , depth = "eye_of_vtull_hillock" },
    { mob = "wind_wraith                        ", level = 61 , max = 2  , depth = "wind_tunnel" },
    { mob = "soul_golem                         ", level = 63 , max = 1  , depth = "temple_of_luukos" },
}
return Spawns
