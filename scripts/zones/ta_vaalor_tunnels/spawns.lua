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

-- Population table (informational — actual loading is per-mob .lua file)
Spawns.population = {
    { mob = "fanged_rodent", level = 1, max = 8, depth = "tunnels" },
    -- cave_gnome / thyril / relnak: max_count=0 until catacomb rooms confirmed
}

return Spawns
