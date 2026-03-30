---------------------------------------------------
-- The Krag Slopes — Spawn Registry
-- scripts/zones/the_krag_slopes/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "the_krag_slopes"
Spawns.area       = "The Krag Slopes"
Spawns.room_range = { min = 6119, max = 8612 }
Spawns.map_locked = true

Spawns.population = {
    -- ── Krag Slopes mid (rooms 6119-6153, level 10) ──────────────────────
    { mob = "gnoll_miner", level = 10, max = 5, depth = "krag_upper" },
    -- ── Krag Slopes deep / Zeltoph (rooms 6134-6153, level 13) ───────────
    { mob = "gnoll_thief", level = 13, max = 6, depth = "krag_deep" },
}






Spawns.mob_rooms = {
    gnoll_miner = {
        6119, 6120, 6121, 6122, 6123, 6124, 6125, 6126, 6127, 6128,
        6129, 6130, 6131, 6132, 6133
    },
    gnoll_thief = {
        6134, 6135, 6136, 6137, 6138, 6139, 6140, 6141, 6142, 6143,
        6144, 6145, 6146, 6147, 6148, 6149, 6150, 6151, 6152, 6153
    },
}

return Spawns
