---------------------------------------------------
-- The Citadel — Spawn Registry
-- scripts/zones/the_citadel/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "the_citadel"
Spawns.area       = "The Citadel / Thurfel's Keep"
Spawns.room_range = { min = 11063, max = 33306 }

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

return Spawns
