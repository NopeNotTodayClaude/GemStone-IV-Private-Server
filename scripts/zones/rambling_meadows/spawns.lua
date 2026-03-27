---------------------------------------------------
-- Rambling Meadows — Spawn Registry
-- scripts/zones/rambling_meadows/spawns.lua
---------------------------------------------------

local Spawns = {}
Spawns.zone       = "rambling_meadows"
Spawns.area       = "Rambling Meadows"
Spawns.room_range = { min = 5950, max = 6030 }

Spawns.population = {
    -- ── Meadow entry (rooms 5950-5957, level 1) ───────────────────────────
    { mob = "young_grass_snake", level = 1, max = 8,  depth = "meadow_entry" },
    { mob = "black_rolton",      level = 1, max = 10, depth = "meadow_entry" },
    { mob = "spotted_gnarp",     level = 1, max = 8,  depth = "meadow_entry" },
    -- ── Meadow mid-entry (rooms 5956-5965, level 2) ───────────────────────
    { mob = "brown_gak",         level = 2, max = 8,  depth = "meadow_mid_entry" },
    { mob = "thyril",            level = 2, max = 6,  depth = "meadow_mid_entry" },
    -- ── Meadow mid (rooms 5969-5993, level 3-5) ───────────────────────────
    { mob = "striped_reinak",    level = 3, max = 8,  depth = "meadow_mid" },
    { mob = "striped_relnak",    level = 3, max = 7,  depth = "meadow_mid" },
    { mob = "spotted_leaper",    level = 4, max = 6,  depth = "meadow_mid" },
    { mob = "coyote",            level = 5, max = 6,  depth = "meadow_mid" },
    -- ── Meadow outer (rooms 5991-6010, level 6-7) ─────────────────────────
    { mob = "spotted_lynx",      level = 6, max = 5,  depth = "meadow_outer" },
    { mob = "lesser_red_orc",    level = 7, max = 6,  depth = "meadow_outer" },
    -- ── Meadow boss (level 22) ────────────────────────────────────────────
    { mob = "crested_basilisk",  level = 22, max = 2, depth = "meadow_boss" },
}

return Spawns
