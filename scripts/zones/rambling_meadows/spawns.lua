---------------------------------------------------
-- Rambling Meadows — Spawn Registry
-- scripts/zones/rambling_meadows/spawns.lua
---------------------------------------------------

local Spawns = {}
Spawns.zone       = "rambling_meadows"
Spawns.area       = "Rambling Meadows"
Spawns.room_range = { min = 5950, max = 6030 }
Spawns.map_locked = true

Spawns.population = {
    -- ── Meadow entry (rooms 5950-5957, level 1) ───────────────────────────
    { mob = "young_grass_snake", level = 1, max = 8,  depth = "meadow_entry" },
    { mob = "black_rolton",      level = 1, max = 10, depth = "meadow_entry" },
    { mob = "spotted_gnarp",     level = 1, max = 8,  depth = "meadow_entry" },
    -- ── Meadow mid-entry (rooms 5956-5965, level 2) ───────────────────────
    { mob = "brown_gak",         level = 2, max = 8,  depth = "meadow_mid_entry" },
    { mob = "thyril_meadows",   level = 2, max = 6,  depth = "meadow_mid_entry" },
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






Spawns.mob_rooms = {
    young_grass_snake = {
        5956, 5957, 5958, 5959, 5960, 5961, 5962
    },
    black_rolton = {
        6012, 6013, 6014, 6016, 6018, 6019, 6020, 6021, 6022, 6023,
        6025, 6026
    },
    spotted_gnarp = {
        6012, 6013, 6014, 6016, 6018, 6019, 6020, 6021, 6022, 6023,
        6025, 6026
    },
    brown_gak = {
        6012, 6013, 6014, 6016, 6018, 6019, 6020, 6021, 6022, 6023,
        6025, 6026
    },
    thyril_meadows = {
        5956, 5957, 5958, 5959, 5960, 5961, 5962, 5963, 5964, 5965,
        5966
    },
    striped_reinak = {
        5985, 5986, 5987, 5988, 5989, 5990, 5991, 5992, 5993, 5970,
        5971, 5972, 5973
    },
    striped_relnak = {
        5970, 5971, 5972, 5973, 5976, 5977, 5978, 5985, 5986, 5987,
        5988, 5989, 5990, 5991, 5992, 5993
    },
    spotted_leaper = {
        5969, 5970, 5971, 5972, 5973, 5976, 5977, 5978, 5979, 5980,
        5981, 5982, 5983, 5984
    },
    coyote = {
        6012, 6023, 6024
    },
    spotted_lynx = {
        6027, 6028, 6029, 6030
    },
    lesser_red_orc = {
        6032, 6033, 6034, 6035, 6036, 6037, 6038, 6039, 6040
    },
    crested_basilisk = {
        6002, 6003, 6004, 6005, 6006, 6007, 6008, 6009
    },
}

return Spawns
