---------------------------------------------------
-- Rivers Rest & Maelstrom Bay — Spawn Registry
-- scripts/zones/rivers_rest/spawns.lua
---------------------------------------------------
local Spawns = {}
Spawns.zone       = "rivers_rest"
Spawns.area       = "Rivers Rest & Maelstrom Bay"
Spawns.room_range = { min = 11531, max = 17692 }
Spawns.map_locked = true
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





Spawns.mob_rooms = {
    moor_hound = {
        11531, 11532, 11533, 11534, 11535, 11536, 11537, 11538, 11539, 11540,
        11548, 11549, 11550, 11551, 11552, 11553
    },
    moor_witch = {
        11531, 11532, 11533, 11534, 11535, 11536, 11537, 11538, 11611, 11612,
        11613, 11614
    },
    moor_eagle = {
        11531, 11532, 11533, 11534, 11535, 11536, 11537, 11538, 11539, 11540,
        11548, 11549, 11550, 11551, 11552, 11553
    },
    spectral_black_warhorse = {
        11531, 11532, 11533, 11534, 11535, 11536, 11537, 11538, 11539, 11540,
        11548, 11549, 11550, 11551, 11552, 11553, 11611, 11612, 11613, 11614,
        11615, 11616
    },
    bog_troll = {
        11611, 11612, 11613, 11614, 11615, 11616, 11617, 11618, 11619, 11620,
        11621, 11622, 11623, 11624, 11625, 11626, 11627, 11628, 11629, 11630,
        11646, 11664, 11665, 11666, 11670, 11675, 11676
    },
    skeletal_soldier = {
        11627, 11628, 11629, 11630, 11631, 11632, 11633, 11634, 11635, 11636,
        11637, 11638, 11639, 11640, 11641, 11642, 11643, 11644, 11645, 11650,
        11646, 11664, 11665, 11666, 11670, 11675, 11676
    },
    luminous_spectre = {
        11647, 11648, 11649, 11658, 11659, 11660, 11661, 11662, 11663, 11646,
        11664, 11665, 11666, 11670, 11675, 11676
    },
}

return Spawns
