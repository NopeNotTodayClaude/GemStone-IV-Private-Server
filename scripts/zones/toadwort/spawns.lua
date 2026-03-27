---------------------------------------------------
-- The Toadwort — Spawn Registry
-- scripts/zones/toadwort/spawns.lua
---------------------------------------------------
-- Swamp zone between Wehnimer's Landing and the Neartofar Forest.
-- Level range: 2-10
-- Source: gswiki.play.net category "Toadwort creatures"
--
-- Sub-areas:
--   Muddy Path         : fanged goblin (2), Mistydeep siren (2)
--   Blackened Morass   : water moccasin (4), fanged viper (4)
--   Fetid Muck & Mire  : bobcat (5)
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "toadwort"
Spawns.area       = "The Toadwort"
Spawns.room_range = { min = 10499, max = 10600 }

Spawns.population = {
    { mob = "fanged_goblin",    level = 2,  max = 6,  depth = "muddy_path" },
    { mob = "mistydeep_siren",  level = 2,  max = 5,  depth = "muddy_path" },
    { mob = "water_moccasin",   level = 4,  max = 6,  depth = "blackened_morass" },
    { mob = "fanged_viper",     level = 4,  max = 6,  depth = "blackened_morass" },
    { mob = "bobcat",           level = 5,  max = 4,  depth = "fetid_muck" },
}

return Spawns
