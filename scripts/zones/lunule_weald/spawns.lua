---------------------------------------------------
-- Lunule Weald — Spawn Registry
-- scripts/zones/lunule_weald/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "lunule_weald"
Spawns.area       = "Lunule Weald"
Spawns.room_range = { min = 10540, max = 10621 }

Spawns.population = {
    { mob = "rotting_farmhand",   level = 13, max = 6,  depth = "slade" },
    { mob = "decaying_farmhand",  level = 14, max = 5,  depth = "slade" },
    { mob = "elder_boar",         level = 14, max = 3,  depth = "knoll" },
    { mob = "puma",               level = 15, max = 4,  depth = "knoll_felwood" },
    { mob = "decaying_woodsman",  level = 15, max = 5,  depth = "felwood_grove" },
    { mob = "fel_wolf",           level = 17, max = 5,  depth = "felwood_deep" },
    { mob = "death_dirge",        level = 18, max = 4,  depth = "perish_glen" },
    { mob = "moaning_phantom",    level = 20, max = 3,  depth = "perish_glen" },
    { mob = "arch_wight",         level = 21, max = 3,  depth = "perish_glen_deep" },
    { mob = "dark_apparition",    level = 23, max = 3,  depth = "zealot_village" },
    { mob = "shadowy_spectre",    level = 25, max = 3,  depth = "zealot_village" },
    { mob = "revenant",           level = 27, max = 2,  depth = "zealot_village_deep" },
}

return Spawns
