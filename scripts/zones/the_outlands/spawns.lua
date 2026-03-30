---------------------------------------------------
-- The Outlands — Spawn Registry
-- Vornavis Holdings open plains
-- scripts/zones/the_outlands/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "the_outlands"
Spawns.area       = "The Outlands / Vornavis Holdings"
Spawns.room_range = { min = 5465, max = 17080 }
Spawns.map_locked = true

Spawns.population = {
    -- ── Open pasture plains (rooms 5465-5494, level 3) ───────────────────
    { mob = "bresnahanini_rolton", level = 3, max = 10, depth = "outlands_pasture" },
}






Spawns.mob_rooms = {
    bresnahanini_rolton = {
        5465, 5466, 5467, 5468, 5469, 5470, 5471, 5472, 5473, 5474,
        5475, 5476, 5477, 5478, 5479, 5480, 5481, 5482, 5483, 5484,
        5485, 5486, 5487, 5488, 5489, 5490, 5491, 5492, 5493, 5494
    },
}

return Spawns
