---------------------------------------------------
-- The Yegharren Plains — Spawn Registry
-- scripts/zones/the_yegharren_plains/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "the_yegharren_plains"
Spawns.area       = "The Yegharren Plains"
Spawns.room_range = { min = 4612, max = 10062 }

Spawns.population = {
    -- ── Open grassland (rooms 4990-5009, level 13) ───────────────────────
    { mob = "tawny_brindlecat", level = 13, max = 6, depth = "high_plains" },
}

return Spawns
