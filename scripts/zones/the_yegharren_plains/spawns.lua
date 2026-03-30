---------------------------------------------------
-- The Yegharren Plains — Spawn Registry
-- scripts/zones/the_yegharren_plains/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "the_yegharren_plains"
Spawns.area       = "The Yegharren Plains"
Spawns.room_range = { min = 4612, max = 10062 }
Spawns.map_locked = true

Spawns.population = {
    -- ── Open grassland (rooms 4990-5009, level 13) ───────────────────────
    { mob = "tawny_brindlecat", level = 13, max = 6, depth = "high_plains" },
}






Spawns.mob_rooms = {
    tawny_brindlecat = {
        4990, 4991, 4992, 4993, 4994, 4995, 4996, 4997, 4998, 4999,
        5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009
    },
}

return Spawns
