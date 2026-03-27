---------------------------------------------------
-- The Cairnfang — Spawn Registry
-- Dense upland forest south of Wehnimer's Landing
-- scripts/zones/the_cairnfang/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "the_cairnfang"
Spawns.area       = "The Cairnfang"
Spawns.room_range = { min = 1372, max = 9376 }

Spawns.population = {
    -- ── Cairnfang Uplands (rooms 1372-1414, level 3) ─────────────────────
    -- The hobgoblin found here is the same mob file as wehnimers_landing —
    -- it spans both areas per wiki ("Cairnfang Forest + Wehnimer's Environs")
    { mob = "hobgoblin", level = 3, max = 7, depth = "cairnfang_uplands" },
}

return Spawns
