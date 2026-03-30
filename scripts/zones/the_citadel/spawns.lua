---------------------------------------------------
-- The Citadel — Spawn Registry
-- scripts/zones/the_citadel/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "the_citadel"
Spawns.area       = "The Citadel / Thurfel's Keep"
Spawns.room_range = { min = 11063, max = 33306 }
Spawns.map_locked = true

Spawns.population = {
    -- ── River Tunnels entry (level 5-7) ───────────────────────────────────
    { mob = "night_golem",     level = 5,  max = 6, depth = "river_tunnels_entry" },
    { mob = "monkey",          level = 6,  max = 5, depth = "river_tunnels_mid" },
    { mob = "blood_eagle",     level = 7,  max = 4, depth = "river_tunnels_upper" },
    -- ── River Tunnels deep (level 8-10) ───────────────────────────────────
    { mob = "crystal_crab",    level = 8,  max = 4, depth = "river_tunnels_deep" },
    { mob = "brown_spinner",   level = 9,  max = 4, depth = "river_tunnels_deephive" },
    { mob = "crocodile",       level = 9,  max = 3, depth = "river_tunnels_flooded" },
    { mob = "rabid_guard_dog", level = 10, max = 4, depth = "river_tunnels_guard" },
    -- ── Thurfel's Keep upper (level 11-13) ────────────────────────────────
    { mob = "wall_guardian",   level = 11, max = 5, depth = "thurfels_keep_upper" },
    { mob = "deranged_sentry", level = 13, max = 5, depth = "thurfels_keep_deep" },
}






Spawns.mob_rooms = {
    night_golem = {
        11063, 11064, 11065, 11066, 11123, 11124, 11125, 11126, 11127, 11128,
        11129, 11130, 11131, 11132, 11133, 11134, 11135, 11136, 11137, 11138,
        11139, 11140, 11141, 11142, 11143, 11144, 11145, 11146, 11147, 11148,
        11149, 11150
    },
    monkey = {
        11151, 11152, 11153, 11154, 11155, 11156, 11157, 11158, 11159, 11160,
        11161, 11162, 11163, 11164, 11165
    },
    blood_eagle = {
        11166, 11167, 11168, 11169, 11170, 11171, 11172, 11173, 11174, 11175,
        11176, 11177, 11178, 11179, 11180
    },
    crystal_crab = {
        11181, 11182, 11183, 11184, 11185, 11186, 11187, 11188, 11189, 11190,
        11191, 11192, 11193, 11194, 11195
    },
    brown_spinner = {
        11196, 11197, 11198, 11199, 11200, 11201, 11202, 11203, 11204, 11205,
        11206, 11207, 11208, 11209, 11210
    },
    crocodile = {
        11211, 11212, 11213, 11214, 11215, 11216, 11217, 11218, 11219, 11220,
        11221, 11222, 11223, 11224, 11225
    },
    rabid_guard_dog = {
        11226, 11227, 11228, 11229, 11230, 11231, 11232, 11233, 11234, 11235,
        11236, 11237, 11238, 11239, 11240
    },
    wall_guardian = {
        11241, 11242, 11243, 11244, 11245, 11246, 11247, 11248, 11249, 11250,
        11251, 11252, 11253, 11254, 11255, 11256, 11257, 11258, 11259, 11260
    },
    deranged_sentry = {
        11261, 11262, 11263, 11264, 11265, 11266, 11267, 11268, 11269, 11270,
        11271, 11272, 11273, 11274, 11275, 11276, 11277, 11278, 11279, 11280
    },
}

return Spawns
