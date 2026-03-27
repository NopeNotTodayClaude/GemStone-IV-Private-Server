---------------------------------------------------
-- The Krag Slopes — Spawn Registry
-- scripts/zones/the_krag_slopes/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "the_krag_slopes"
Spawns.area       = "The Krag Slopes"
Spawns.room_range = { min = 6119, max = 8612 }

Spawns.population = {
    -- ── Krag Slopes mid (rooms 6119-6153, level 10) ──────────────────────
    { mob = "gnoll_miner", level = 10, max = 5, depth = "krag_upper" },
    -- ── Krag Slopes deep / Zeltoph (rooms 6134-6153, level 13) ───────────
    { mob = "gnoll_thief", level = 13, max = 6, depth = "krag_deep" },
}

return Spawns
