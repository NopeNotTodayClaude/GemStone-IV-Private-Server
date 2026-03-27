---------------------------------------------------
-- The Outlands — Spawn Registry
-- Vornavis Holdings open plains
-- scripts/zones/the_outlands/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "the_outlands"
Spawns.area       = "The Outlands / Vornavis Holdings"
Spawns.room_range = { min = 5465, max = 17080 }

Spawns.population = {
    -- ── Open pasture plains (rooms 5465-5494, level 3) ───────────────────
    { mob = "bresnahanini_rolton", level = 3, max = 10, depth = "outlands_pasture" },
}

return Spawns
