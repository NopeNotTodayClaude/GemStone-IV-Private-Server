---------------------------------------------------
-- The Cairnfang — Spawn Registry
-- Dense upland forest south of Wehnimer's Landing
-- scripts/zones/the_cairnfang/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "the_cairnfang"
Spawns.area       = "The Cairnfang"
Spawns.room_range = { min = 1372, max = 9376 }
Spawns.map_locked = true

Spawns.population = {
    -- ── Cairnfang Uplands (rooms 1372-1414, level 3) ─────────────────────
    -- The hobgoblin found here is the same mob file as wehnimers_landing —
    -- it spans both areas per wiki ("Cairnfang Forest + Wehnimer's Environs")
    { mob = "hobgoblin", level = 3, max = 7, depth = "cairnfang_uplands" },
}

Spawns.mob_rooms = {
    hobgoblin = {
        1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381,
        1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391,
        1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401,
        1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411,
        1412, 1413, 1414
    },
}

return Spawns
