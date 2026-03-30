-- Icemule Trace / Glatoph Spawn Registry
local Spawns={}
Spawns.zone="icemule_trace"; Spawns.area="Icemule Trace / Glatoph"
Spawns.room_range={min=3195,max=30519}
Spawns.map_locked = true
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





Spawns.mob_rooms = {
    rolton = {
        3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202
    },
    kobold_imt = {
        3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204,
        3205, 3206
    },
    carrion_worm = {
        3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204,
        3205, 3206
    },
    zombie_rolton = {
        3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204,
        3205, 3206
    },
    rabid_squirrel = {
        3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204,
        3205, 3206, 3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214,
        3215, 3216, 3217
    },
    lesser_frost_shade = {
        3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204,
        3205, 3206
    },
    white_vysan = {
        3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204,
        3205, 3206
    },
    ice_skeleton = {
        3678, 3679, 3680, 3681, 3682, 4122
    },
    greater_ice_spider = {
        3678, 3679, 3680, 3681, 3682, 4122
    },
    leaper = {
        2558, 2559, 2560, 2561, 2562, 2563, 2564, 2565, 2566, 2567,
        2568, 2569, 2570, 2571, 2572
    },
    snowy_cockatrice = {
        2570, 2571, 2572, 2573, 2574, 2575, 2576, 2577, 2578, 2579,
        2580, 2581, 2582, 2583, 2584
    },
    great_brown_bear = {
        3550, 3551, 3552, 3553, 3554, 3559, 3617
    },
    grey_orc_glatoph = {
        3678, 3679, 3680, 3681, 3682, 4122, 4123, 4124, 4125, 4126,
        4127, 4128, 4129, 4130, 4131, 4132, 4133
    },
    hill_troll = {
        3678, 3679, 3680, 3681, 3682, 4122, 4123, 4124, 4125, 4126,
        4127, 4128, 4129, 4130, 4131, 4132, 4133, 7821, 7824, 7825,
        7826, 7827, 7828, 7829, 7830
    },
    cave_troll_glatoph = {
        7835, 7836, 7837, 7838, 7839, 7840, 7841, 7842, 7843, 7844,
        7845, 7846, 7847, 7848, 7849, 7850
    },
    mountain_ogre = {
        7843, 7844, 7845, 7846, 7847, 7848, 7849, 7850, 7851, 7853,
        7854, 7855, 7856, 7857, 7858, 7859, 7860, 7861, 7867, 7868,
        7869, 7870, 7871, 7872, 7902, 7903, 7904, 7905, 30516, 30517,
        30518, 30519
    },
    ghost_wolf = {
        3211, 3212, 3213, 3214, 3215, 3216, 3217
    },
    war_troll = {
        7821, 7824, 7825, 7826, 7827, 7828, 7829, 7830, 7831, 7832,
        7833, 7834, 7835, 7836, 7837, 7838, 7839, 7840
    },
    ice_hound = {
        3550, 3551, 3552, 3553, 3554, 3559, 3617, 3678, 3679, 3680,
        3681, 3682, 4122, 4123, 4124
    },
    ice_troll = {
        3550, 3551, 3552, 3553, 3554, 3559, 3617, 3678, 3679, 3680,
        3681, 3682, 4122, 4123, 4124
    },
    cold_guardian = {
        7848, 7849, 7850, 7851, 7853, 7854, 7855, 7856, 7857, 7858,
        7859, 7860, 7861, 7867, 7868
    },
    snow_spectre = {
        2585, 2586, 2587, 2588, 2589, 2590, 2591, 2592, 2593, 2594,
        2595, 2596, 2597, 2598, 2599
    },
}

return Spawns
