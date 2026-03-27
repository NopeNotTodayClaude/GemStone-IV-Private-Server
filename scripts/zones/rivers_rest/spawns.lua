---------------------------------------------------
-- Rivers Rest & Maelstrom Bay — Spawn Registry
-- scripts/zones/rivers_rest/spawns.lua
---------------------------------------------------
local Spawns = {}
Spawns.zone       = "rivers_rest"
Spawns.area       = "Rivers Rest & Maelstrom Bay"
Spawns.room_range = { min = 11531, max = 17692 }
Spawns.population = {
    { mob = "moor_hound                         ", level = 33 , max = 6  , depth = "shattered_moors" },
    { mob = "moor_witch                         ", level = 34 , max = 3  , depth = "shattered_moors" },
    { mob = "moor_eagle                         ", level = 35 , max = 4  , depth = "shattered_moors" },
    { mob = "spectral_black_warhorse            ", level = 35 , max = 2  , depth = "shattered_moors_deep" },
    { mob = "bog_troll                          ", level = 35 , max = 5  , depth = "miasmal_forest" },
    { mob = "skeletal_soldier                   ", level = 34 , max = 5  , depth = "miasmal_forest" },
    { mob = "lesser_moor_wight                  ", level = 37 , max = 4  , depth = "miasmal_forest_deep" },
    { mob = "bog_wraith                         ", level = 41 , max = 3  , depth = "miasmal_forest_deep" },
    { mob = "luminous_spectre                   ", level = 35 , max = 3  , depth = "ghastly_swamp" },
    { mob = "greater_bog_troll                  ", level = 39 , max = 4  , depth = "oteskas_haven" },
    { mob = "greater_moor_wight                 ", level = 39 , max = 3  , depth = "oteskas_haven" },
    { mob = "swamp_hag                          ", level = 42 , max = 2  , depth = "oteskas_haven" },
    { mob = "greater_fetid_corpse               ", level = 42 , max = 3  , depth = "oteskas_haven" },
    { mob = "gaunt_spectral_servant             ", level = 44 , max = 5  , depth = "marsh_keep_fen" },
    { mob = "rotting_chimera                    ", level = 46 , max = 2  , depth = "marsh_keep_interior" },
    { mob = "necrotic_snake                     ", level = 48 , max = 3  , depth = "marsh_keep_deep" },
    { mob = "flesh_golem                        ", level = 50 , max = 2  , depth = "marsh_keep_deep" },
    { mob = "tomb_troll                         ", level = 52 , max = 3  , depth = "marsh_keep_deepest" },
    { mob = "tomb_troll_necromancer             ", level = 54 , max = 1  , depth = "marsh_keep_deepest" },
}
return Spawns
