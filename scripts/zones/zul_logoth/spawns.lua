---------------------------------------------------
-- Zul Logoth / Zaerthu & Mraent — Spawn Registry
-- scripts/zones/zul_logoth/spawns.lua
---------------------------------------------------
local Spawns = {}
Spawns.zone       = "zul_logoth"
Spawns.area       = "Zul Logoth / Zaerthu & Mraent"
Spawns.room_range = { min = 1018, max = 9468 }
Spawns.map_locked = true
Spawns.population = {
    { mob = "roa_ter_zaerthu                    ", level = 24 , max = 5  , depth = "zaerthu_tunnels" },
    { mob = "grutik_savage                      ", level = 27 , max = 5  , depth = "zaerthu_tunnels" },
    { mob = "grutik_shaman                      ", level = 29 , max = 3  , depth = "zaerthu_tunnels_deep" },
    { mob = "troll_wraith                       ", level = 35 , max = 3  , depth = "troll_burial_grounds" },
    { mob = "rock_troll_zombie                  ", level = 34 , max = 4  , depth = "troll_burial_grounds" },
    { mob = "undertaker_bat                     ", level = 36 , max = 5  , depth = "mraent_cavern" },
    { mob = "giant_albino_scorpion              ", level = 24 , max = 4  , depth = "mraent_cavern" },
    { mob = "krynch                             ", level = 31 , max = 3  , depth = "mraent_cavern_deep" },
    { mob = "krolvin_warrior                    ", level = 19 , max = 5  , depth = "western_dragonspine" },
    { mob = "krolvin_warfarer                   ", level = 25 , max = 4  , depth = "western_dragonspine_deep" },
}





Spawns.mob_rooms = {
    roa_ter_zaerthu = {
        5787, 5788, 5789, 5790, 5791, 5792, 5793, 5794, 5795, 5796,
        5797, 5798, 5799, 5800, 5801, 5802, 5803, 5804, 5805, 5806
    },
    grutik_savage = {
        5782, 5783, 5784, 5785, 5786, 5787, 5788, 5789, 5790, 5791,
        5792, 5793, 5794, 5795, 5796, 5797, 5798, 5799, 5800, 5801
    },
    grutik_shaman = {
        5792, 5793, 5794, 5795, 5796, 5797, 5798, 5799, 5800, 5801,
        5802, 5803, 5804, 5805, 5806, 5807, 5808, 5809, 5810, 5811
    },
    troll_wraith = {
        5811, 5812, 5813, 5814, 5815, 5816, 5817, 5818, 5819, 5820,
        5821, 5822
    },
    rock_troll_zombie = {
        5808, 5809, 5810, 5811, 5812, 5813, 5814, 5815, 5816, 5817,
        5818, 5819, 5820, 5821, 5822, 5752, 5753, 5754, 5756
    },
    giant_albino_scorpion = {
        5752, 5753, 5754, 5756, 5757, 5758, 5759, 5760, 5761, 5762,
        5763, 5764, 5770, 5771, 5772, 5773, 5774, 5775, 5776, 5777,
        5778, 5779, 5780, 5781, 9459, 9460, 9461, 9462, 9463, 9464,
        9465, 9466, 9467, 9468
    },
    krynch = {
        5776, 5777, 5778, 5779, 5780, 5781, 9459, 9460, 9461, 9462,
        9463, 9464, 9465, 9466, 9467, 9468
    },
    krolvin_warrior = {
        1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025
    },
    krolvin_warfarer = {
        1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031
    },
}

return Spawns
