-- Icemule Trace / Glatoph Spawn Registry
local Spawns={}
Spawns.zone="icemule_trace"; Spawns.area="Icemule Trace / Glatoph"
Spawns.room_range={min=3195,max=30519}
Spawns.population = {
    { mob="rolton", level=1, max=12, depth="snowy_forest" },
    { mob="kobold_imt", level=1, max=10, depth="snowy_forest" },
    { mob="carrion_worm", level=1, max=6, depth="snowy_forest" },
    { mob="zombie_rolton", level=1, max=6, depth="snowy_forest" },
    { mob="rabid_squirrel", level=2, max=10, depth="snowy_forest" },
    { mob="lesser_frost_shade", level=2, max=5, depth="snowy_forest" },
    { mob="white_vysan", level=3, max=6, depth="snowy_forest" },
    { mob="ice_skeleton", level=3, max=8, depth="glatoph_lower" },
    { mob="greater_ice_spider", level=3, max=6, depth="glatoph_lower" },
    { mob="leaper", level=6, max=5, depth="snowflake_vale" },
    { mob="snowy_cockatrice", level=6, max=5, depth="snowflake_vale" },
    { mob="great_brown_bear", level=14, max=4, depth="glatoph_lower" },
    { mob="grey_orc_glatoph", level=14, max=5, depth="glatoph_mid" },
    { mob="hill_troll", level=16, max=4, depth="glatoph_mid" },
    { mob="cave_troll_glatoph", level=16, max=4, depth="glatoph_mid" },
    { mob="mountain_ogre", level=16, max=4, depth="glatoph_mid" },
    { mob="ghost_wolf", level=16, max=4, depth="tundra" },
    { mob="war_troll", level=18, max=4, depth="glatoph_deep" },
    { mob="ice_hound", level=24, max=6, depth="icy_ravine" },
    { mob="ice_troll", level=29, max=4, depth="glatoph_mid_deep" },
    { mob="cold_guardian", level=34, max=3, depth="cave_of_ice" },
    { mob="arctic_titan", level=36, max=2, depth="glatoph_deep_freeze" },
    { mob="snow_crone", level=36, max=2, depth="glatoph_deep_freeze" },
    { mob="snow_spectre", level=9, max=4, depth="glatoph_upper" },
    { mob="frost_giant", level=38, max=2, depth="glatoph_deep_freeze" },
}
return Spawns
