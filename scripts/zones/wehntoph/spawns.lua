---------------------------------------------------
-- Wehntoph — Spawn Registry
-- Twin Canyons area northeast of Wehnimer's Landing
-- scripts/zones/wehntoph/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "wehntoph"
Spawns.area       = "Wehntoph / Twin Canyons"
Spawns.room_range = { min = 6110, max = 14725 }
Spawns.map_locked = true

Spawns.population = {
    -- ── Lower canyon floor (rooms 6110-6118, level 1) ────────────────────
    { mob = "slimy_little_grub",   level = 1, max = 12, depth = "canyon_floor" },
    -- ── Mid canyon / overlook (rooms 6110-7921, level 5) ─────────────────
    { mob = "nasty_little_gremlin",level = 5, max = 8,  depth = "canyon_mid" },
}






Spawns.mob_rooms = {
    slimy_little_grub = {
        6110, 6111, 6112, 6113, 6114, 6115, 6116, 6117, 6118
    },
    nasty_little_gremlin = {
        6110, 6111, 6112, 6113, 6114, 6115, 6116, 6117, 6118, 7917,
        7918, 7919, 7920, 7921
    },
}

return Spawns
