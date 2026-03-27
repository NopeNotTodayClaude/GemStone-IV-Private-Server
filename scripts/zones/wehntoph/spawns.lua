---------------------------------------------------
-- Wehntoph — Spawn Registry
-- Twin Canyons area northeast of Wehnimer's Landing
-- scripts/zones/wehntoph/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "wehntoph"
Spawns.area       = "Wehntoph / Twin Canyons"
Spawns.room_range = { min = 6110, max = 14725 }

Spawns.population = {
    -- ── Lower canyon floor (rooms 6110-6118, level 1) ────────────────────
    { mob = "slimy_little_grub",   level = 1, max = 12, depth = "canyon_floor" },
    -- ── Mid canyon / overlook (rooms 6110-7921, level 5) ─────────────────
    { mob = "nasty_little_gremlin",level = 5, max = 8,  depth = "canyon_mid" },
}

return Spawns
