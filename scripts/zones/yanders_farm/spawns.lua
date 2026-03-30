---------------------------------------------------
-- Yander's Farm — Spawn Registry
-- scripts/zones/yanders_farm/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "yanders_farm"
Spawns.area       = "Yander's Farm"
Spawns.room_range = { min = 6012, max = 10486 }
Spawns.map_locked = true

-- Population table (informational — actual loading is per-mob .lua file)
Spawns.population = {
    { mob = "great_boar                    ", level = 10 , max = 5  , depth = "wheat_fields" },
    { mob = "giant_marmot                  ", level = 10 , max = 6  , depth = "wheat_barley" },
    { mob = "raider_orc                    ", level = 10 , max = 6  , depth = "wheat_barley" },
    { mob = "dark_orc                      ", level = 12 , max = 5  , depth = "corn_fields" },
    { mob = "great_stag                    ", level = 13 , max = 4  , depth = "corn_barley" },
    { mob = "grey_orc                      ", level = 14 , max = 5  , depth = "corn_barley_deep" },
}






Spawns.mob_rooms = {
    great_boar = {
        6073, 6074, 6075, 6076, 6077, 6078, 6079, 6080, 6081, 6082,
        6083, 6084, 6085, 6086, 6087, 6088, 6089
    },
    giant_marmot = {
        6073, 6074, 6075, 6076, 6077, 6078, 6079, 6080, 6081, 6082,
        6083, 6084, 6085, 6086, 6087, 6088, 6089, 6060, 6061, 6062,
        6063
    },
    raider_orc = {
        6073, 6074, 6075, 6076, 6077, 6078, 6079, 6080, 6081, 6082,
        6083, 6084, 6085, 6086, 6087, 6088, 6089, 6060, 6061, 6062,
        6063, 6064, 6065, 6066, 6067, 6068, 6069, 6070, 6071, 6072,
        10261
    },
    dark_orc = {
        6045, 6046, 6047, 6048, 6049, 6050, 6051, 6052, 6053, 6054,
        6055, 6056, 6057, 6058, 6059
    },
    great_stag = {
        6045, 6046, 6047, 6048, 6049, 6050, 6051, 6052, 6053, 6054,
        6055, 6056, 6057, 6058, 6059, 6068, 6069, 6070, 6071, 6072,
        10261
    },
    grey_orc = {
        6045, 6046, 6047, 6048, 6049, 6050, 6051, 6052, 6053, 6054,
        6055, 6056, 6057, 6058, 6059, 6068, 6069, 6070, 6071, 6072,
        10261
    },
}

return Spawns
