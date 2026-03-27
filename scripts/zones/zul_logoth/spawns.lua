---------------------------------------------------
-- Zul Logoth / Zaerthu & Mraent — Spawn Registry
-- scripts/zones/zul_logoth/spawns.lua
---------------------------------------------------
local Spawns = {}
Spawns.zone       = "zul_logoth"
Spawns.area       = "Zul Logoth / Zaerthu & Mraent"
Spawns.room_range = { min = 1018, max = 9468 }
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
return Spawns
