---------------------------------------------------
-- Grasslands & Foothills — Spawn Registry
-- scripts/zones/grasslands/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "grasslands"
Spawns.area       = "Grasslands & Foothills"
Spawns.room_range = { min = 10171, max = 10267 }
Spawns.map_locked = true

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






Spawns.mob_rooms = {
    agresh_troll_scout = {
        10208, 10209, 10210, 10211, 10212, 10213, 10214, 10215, 10233, 10234,
        10235, 10236, 10237, 10238, 10239, 10261
    },
    black_leopard = {
        10171, 10172, 10173, 10174, 10175, 10176, 10177, 10178, 10179, 10180,
        10181, 10182, 10185, 10186, 10187, 10188, 10216, 10217, 10218, 10219,
        10220, 10221, 10222, 10223, 10224, 10225, 10226, 10227, 10228, 10229,
        10230, 10231, 10232, 10253, 10254, 10255, 10256, 10257, 10258, 10259,
        10260
    },
    agresh_bear = {
        10216, 10217, 10218, 10219, 10220, 10221, 10222, 10223, 10224, 10225,
        10226, 10227, 10228, 10229, 10230, 10231, 10232, 10253, 10254, 10255,
        10256, 10257, 10258, 10259, 10260
    },
    agresh_troll_warrior = {
        10240, 10241, 10242, 10243, 10244, 10245, 10246, 10247, 10248, 10249,
        10250, 10251, 10252, 10262, 10263, 10264, 10265, 10266, 10267
    },
    plains_ogre = {
        10171, 10172, 10173, 10174, 10175, 10176, 10177, 10178, 10179, 10180,
        10181, 10182, 10185, 10186, 10187, 10188, 10183, 10184, 10189, 10190,
        10191, 10192, 10193, 10194, 10195, 10196, 10197, 10198, 10199, 10200,
        10201, 10202, 10203, 10204, 10205, 10206, 10207
    },
    plains_lion = {
        10171, 10172, 10173, 10174, 10175, 10176, 10177, 10178, 10179, 10180,
        10181, 10182, 10185, 10186, 10187, 10188, 10183, 10184, 10189, 10190,
        10191, 10192, 10193, 10194, 10195, 10196, 10197, 10198, 10199, 10200,
        10201, 10202, 10203, 10204, 10205, 10206, 10207
    },
    agresh_troll_chieftain = {
        10171, 10172, 10173, 10174, 10175, 10176, 10177, 10178, 10179, 10180,
        10181, 10182, 10185, 10186, 10187, 10188, 10183, 10184, 10189, 10190,
        10191, 10192, 10193, 10194
    },
}

return Spawns
