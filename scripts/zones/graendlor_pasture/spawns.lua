---------------------------------------------------
-- Graendlor Pasture — Spawn Registry
-- West of Wehnimer's Landing, includes Kobold Village area
-- scripts/zones/graendlor_pasture/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "graendlor_pasture"
Spawns.area       = "Graendlor Pasture"
Spawns.room_range = { min = 358, max = 6761 }

-- NOTE: The big ugly kobold (L2) and kobold shepherd (L3) that inhabit
-- the Kobold Village / Kobold Mines area are in rooms 7999-8021 which
-- belong to zone_id 15 (wehnimers_landing) per the DB.
-- Their mob files live in scripts/zones/wehnimers_landing/mobs/ and
-- their entries in wehnimers_landing/spawns.lua accordingly.
-- This pasture zone currently has no confirmed hunting creatures with
-- available wiki stats. To be populated when source data is available.
Spawns.population = {}

return Spawns
