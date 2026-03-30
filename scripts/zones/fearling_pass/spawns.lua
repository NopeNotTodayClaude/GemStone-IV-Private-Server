---------------------------------------------------
-- Fearling Pass & Barefoot Hill — Spawn Registry
-- scripts/zones/fearling_pass/spawns.lua
---------------------------------------------------
-- Hunting areas near Ta'Vaalor (level 1)
--   Barefoot Hill  : fire ants (level 1)
--   Briar Thicket  : kobolds   (level 1)
--
-- NOTE: The cobbled road / rocky trail kobolds (rooms 3557, 6101, 10121-10165)
--       are handled by scripts/zones/tavaalor/mobs/kobold.lua (ID 7010).
--       The thyril entry that was here previously is NOT confirmed in Fearling
--       Pass per gswiki.play.net/Thyril — removed.
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "fearling_pass"
Spawns.area       = "Fearling Pass, Barefoot Hill & Briar Thicket"
Spawns.room_range = { min = 3557, max = 15939 }
Spawns.map_locked = true

Spawns.population = {
    { mob = "fire_ant", level = 1, max = 10, depth = "barefoot_hill" },
    { mob = "kobold",   level = 1, max = 8,  depth = "briar_thicket" },
}






Spawns.mob_rooms = {
    fire_ant = {
        6090, 6091, 6092, 6093, 6094, 6095, 6096, 6097, 6098, 6099,
        6100, 10269, 10290, 10291, 10292, 10295, 10296, 10297
    },
    kobold = {
        10166, 10167, 10168, 10169, 10170, 10270
    },
}

return Spawns
