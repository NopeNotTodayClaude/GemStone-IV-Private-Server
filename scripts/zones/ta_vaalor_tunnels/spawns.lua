---------------------------------------------------
-- Ta'Vaalor Tunnels — Spawn Registry
-- scripts/zones/ta_vaalor_tunnels/spawns.lua
---------------------------------------------------
-- Rooms 5900-5940: service tunnels and shallow catacombs beneath Ta'Vaalor
-- Level 1 hunting area — entry-level characters.
--
-- AUTHORITATIVE spawn assignment for this room range:
--   fanged_rodent  — rooms 5900-5940  (ONLY creature here)
--
-- cave_gnome, thyril, relnak: defined in this zone's mobs/ folder
-- but have max_count=0 and empty spawn_rooms until their correct
-- catacomb rooms are confirmed and added to their respective lua files.
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "ta_vaalor_tunnels"
Spawns.area       = "Ta'Vaalor Tunnels (rooms 5900-5940)"
Spawns.room_range = { min = 5900, max = 5940 }
Spawns.map_locked = true

-- Population table (informational — actual loading is per-mob .lua file)
Spawns.population = {
    { mob = "fanged_rodent", level = 1, max = 8, depth = "tunnels" },
    -- cave_gnome / thyril / relnak: max_count=0 until catacomb rooms confirmed
}






Spawns.mob_rooms = {
    fanged_rodent = {
        5900, 5901, 5902, 5903, 5904, 5905, 5906, 5907, 5908, 5909,
        5910, 5911, 5912, 5913, 5914, 5915, 5916, 5917, 5918, 5919,
        5920, 5921, 5922, 5923, 5924, 5925, 5926, 5927, 5928, 5929,
        5930, 5931, 5932, 5933, 5934, 5935, 5936, 5937, 5938, 5939,
        5940
    },
}

return Spawns
