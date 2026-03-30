---------------------------------------------------
-- Teras Isle / Fhorian Village — Spawn Registry
-- scripts/zones/teras_isle/spawns.lua
---------------------------------------------------
local Spawns = {}
Spawns.zone       = "teras_isle"
Spawns.area       = "Teras Isle / Fhorian Village"
Spawns.room_range = { min = 1998, max = 12767 }
Spawns.map_locked = true
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





Spawns.mob_rooms = {
    jungle_troll = {
        1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007,
        2008, 2009, 2010, 2021, 2022, 2023, 2041, 2042
    },
    giant_fog_beetle = {
        1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007,
        2008, 2009, 2010, 2021, 2022, 2023, 2041, 2042, 2043, 2044,
        2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 12569, 12570,
        2030, 2031, 2032, 2033
    },
    jungle_troll_chieftain = {
        2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 12569, 12570,
        2030, 2031, 2032
    },
    scaly_burgee = {
        2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020,
        12575, 12576, 12577, 12578
    },
    fire_ogre = {
        2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020,
        12575, 12576, 12577, 12578, 12579, 12580, 12581
    },
    ash_hag = {
        12575, 12576, 12577, 12578, 12579, 12580, 12581
    },
    lava_troll = {
        12579, 12580, 12581
    },
}

return Spawns
