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
Spawns.map_locked = true

Spawns.population = {
    { mob = "fanged_goblin",    level = 2,  max = 6,  depth = "muddy_path" },
    { mob = "mistydeep_siren",  level = 2,  max = 5,  depth = "muddy_path" },
    { mob = "water_moccasin",   level = 4,  max = 6,  depth = "blackened_morass" },
    { mob = "fanged_viper",     level = 4,  max = 6,  depth = "blackened_morass" },
    { mob = "bobcat",           level = 5,  max = 4,  depth = "fetid_muck" },
}






Spawns.mob_rooms = {
    fanged_goblin = {
        10499, 10500, 10501, 10502, 10503, 10504, 10505, 10506, 10507, 10508
    },
    mistydeep_siren = {
        10510, 10511, 10512, 10513, 10514, 10515, 10516, 10517, 10518, 10519,
        10520, 10521, 10522
    },
    water_moccasin = {
        10523, 10524, 10525, 10526, 10527, 10528, 10529, 10530, 10531, 10532,
        10533, 10534
    },
    fanged_viper = {
        10505, 10506, 10507, 10508, 10509, 10510, 10511, 10512, 10513, 10514,
        10515, 10516, 10517, 10518, 10519, 10520, 10521, 10522, 10523
    },
    bobcat = {
        10499, 10500, 10501, 10502, 10503, 10504, 10531, 10532, 10533, 10534,
        10535, 10536, 10537, 10538, 10539
    },
}

return Spawns
