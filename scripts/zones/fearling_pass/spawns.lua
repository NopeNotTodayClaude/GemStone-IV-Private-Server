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

Spawns.population = {
    { mob = "fire_ant", level = 1, max = 10, depth = "barefoot_hill" },
    { mob = "kobold",   level = 1, max = 8,  depth = "briar_thicket" },
}

return Spawns
