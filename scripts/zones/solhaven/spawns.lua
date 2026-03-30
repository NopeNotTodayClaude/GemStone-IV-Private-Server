---------------------------------------------------
-- Solhaven / Vornavis Coast — Spawn Registry
-- scripts/zones/solhaven/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "solhaven"
Spawns.area       = "Solhaven / Vornavis Coast"
Spawns.room_range = { min = 151, max = 7755 }
Spawns.map_locked = true

Spawns.population = {
    -- ── Coastal Cliffs lower (level 1-2) ──────────────────────────────────
    { mob = "kobold",                  level = 1,  max = 10, depth = "coastal_cliffs_low" },
    { mob = "black_winged_daggerbeak", level = 1,  max = 8,  depth = "coastal_cliffs_low" },
    { mob = "carrion_worm",            level = 1,  max = 6,  depth = "coastal_cliffs_low" },
    { mob = "ghost",                   level = 2,  max = 5,  depth = "coastal_cliffs_low" },
    { mob = "pale_crab",               level = 2,  max = 7,  depth = "coastal_cliffs_low" },
    { mob = "sea_nymph",               level = 2,  max = 6,  depth = "coastal_cliffs_low" },
    -- ── Vornavian Coast / Mid-cliffs (level 3-5) ─────────────────────────
    { mob = "fire_salamander_beach",   level = 3,  max = 7,  depth = "north_beach" },
    { mob = "cobra",                   level = 4,  max = 6,  depth = "vornavian_coast" },
    { mob = "mongrel_kobold",          level = 4,  max = 8,  depth = "coastal_cliffs_mid" },
    { mob = "urgh",                    level = 4,  max = 8,  depth = "coastal_cliffs_mid" },
    { mob = "whiptail",                level = 4,  max = 5,  depth = "vornavian_coast" },
    { mob = "water_witch",             level = 5,  max = 5,  depth = "lower_dragonsclaw" },
    -- ── Upper cliffs (level 6-9) ───────────────────────────────────────────
    { mob = "leaper",                  level = 6,  max = 5,  depth = "coastal_cliffs_upper" },
    { mob = "spectral_fisherman",      level = 6,  max = 5,  depth = "vornavian_coast" },
    { mob = "firephantom",             level = 6,  max = 5,  depth = "north_beach_lagoon" },
    { mob = "greater_kappa",           level = 7,  max = 5,  depth = "coastal_cliffs_upper" },
    { mob = "shelfae_soldier",         level = 7,  max = 5,  depth = "coastal_cliffs_upper" },
    { mob = "thrak",                   level = 8,  max = 5,  depth = "coastal_cliffs_upper" },
    { mob = "mottled_thrak",           level = 8,  max = 4,  depth = "coastal_cliffs_upper" },
    { mob = "greater_spider",          level = 8,  max = 7,  depth = "caverns" },
    { mob = "manticore",               level = 9,  max = 4,  depth = "coastal_cliffs_upper" },
    -- ── Upper cliffs / Dragonsclaw (level 11) ─────────────────────────────
    { mob = "shelfae_chieftain",       level = 11, max = 4,  depth = "coastal_cliffs_upper" },
    -- ── Mossy Caverns / Dragonsclaw (level 14-17) ─────────────────────────
    { mob = "specter_beach",           level = 14, max = 4,  depth = "mossy_caverns" },
    { mob = "forest_troll_dragonsclaw",level = 14, max = 4,  depth = "lower_dragonsclaw_deep" },
    { mob = "cave_troll",              level = 16, max = 4,  depth = "north_beach_caverns" },
    { mob = "fire_guardian",           level = 16, max = 4,  depth = "north_beach" },
    { mob = "dark_shambler_beach",     level = 17, max = 3,  depth = "north_beach_lagoon" },
    -- ── North beach lagoon deep (level 33) ───────────────────────────────
    { mob = "sand_beetle",             level = 33, max = 2,  depth = "north_beach_lagoon_deep" },
}






Spawns.mob_rooms = {
    kobold = {
        478, 479, 480, 481, 482, 483, 484, 485, 486, 487,
        488, 489, 490, 491, 492, 493
    },
    black_winged_daggerbeak = {
        478, 479, 480, 481, 482, 483, 484, 485, 486, 487,
        488, 489, 490, 491, 492, 493
    },
    carrion_worm = {
        478, 479, 480, 481, 482, 483, 484, 485, 486, 487,
        488, 489, 490, 491, 492, 493
    },
    ghost = {
        478, 479, 480, 481, 482, 483, 484, 485, 486, 487,
        488, 489, 490, 491, 492, 493
    },
    pale_crab = {
        478, 479, 480, 481, 482, 483, 484, 485, 486, 487,
        488, 489, 490, 491, 492, 493
    },
    sea_nymph = {
        478, 479, 480, 481, 482, 483, 484, 485, 486, 487,
        488, 489, 490, 491, 492, 493
    },
    fire_salamander_beach = {
        7603, 7604, 7605, 7606, 7607, 7608, 7613, 7615
    },
    cobra = {
        7601, 7673, 7674, 7675, 7676, 7677, 7678, 7679, 7680, 7681
    },
    mongrel_kobold = {
        486, 487, 488, 489, 490, 491, 492, 493, 494, 495,
        496, 497, 498, 499, 500, 501, 502, 503, 504, 505,
        506, 507, 508, 509, 510, 511, 512, 513, 514, 515,
        516, 517, 518, 519, 520, 521, 522, 523, 524, 525,
        7601, 7673, 7674, 7675, 7676, 7677, 7678, 7679, 7680, 7681,
        213, 214, 215, 216, 217, 218, 219, 421
    },
    urgh = {
        7601, 7673, 7674, 7675, 7676, 7677, 7678, 7679, 7680, 7681,
        213, 214, 215, 216, 217, 218
    },
    whiptail = {
        7601, 7673, 7674, 7675, 7676, 7677, 7678, 7679, 7680, 7681
    },
    water_witch = {
        213, 214, 215, 216, 217, 218, 219, 421, 422, 423,
        424, 425
    },
    leaper = {
        7707, 7712, 7713, 7714, 7715, 7716, 7717, 7718, 7719, 7720,
        7721, 7722, 7723, 7724, 7725
    },
    spectral_fisherman = {
        7673, 7674, 7675, 7676, 7677, 7678, 7679, 7680, 7681, 7601
    },
    firephantom = {
        7613, 7615, 7616, 7619, 7632, 7633, 7634, 7637, 7638, 7639,
        7640, 7641, 7642, 7643, 7644, 7654, 7707, 7712, 7713, 7714
    },
    greater_kappa = {
        7707, 7712, 7713, 7714, 7715, 7716, 7717, 7718, 7719, 7720,
        7721, 7722, 7723, 7724, 7725
    },
    shelfae_soldier = {
        7726, 7727, 7728, 7729, 7730, 7731, 7732, 7733, 7734, 7735,
        7736, 7737, 7738, 7739, 7740
    },
    thrak = {
        522, 523, 524, 525, 7601, 7673, 7674, 7675, 7676, 7677,
        7678, 7679, 7680, 7681
    },
    mottled_thrak = {
        7707, 7712, 7713, 7714, 7715, 7716, 7717, 7718, 7719, 7720,
        7721, 7722, 7723, 7724, 7725
    },
    greater_spider = {
        7707, 7712, 7713, 7714, 7715, 7716, 7717, 7718, 7719, 7720,
        7721, 7722, 7723, 7724, 7725, 7726, 7727, 7728, 7729, 7730,
        7731, 7732, 7733, 7734, 7735, 7736, 7737, 7738, 7739, 7740,
        7741, 7742, 7743, 7744, 7745, 7746, 7747, 7748, 7749, 7750,
        7751, 7752, 7753, 7754, 7755
    },
    manticore = {
        7601, 7673, 7674, 7675, 7676, 7677, 7678, 7679, 7680, 7681
    },
    shelfae_chieftain = {
        7726, 7727, 7728, 7729, 7730, 7731, 7732, 7733, 7734, 7735,
        7736, 7737, 7738, 7739, 7740, 7741, 7742, 7743, 7744, 7745
    },
    specter_beach = {
        7734, 7735, 7736, 7737, 7738, 7739, 7740, 7741, 7742, 7743,
        7744, 7745, 7746, 7747, 7748, 7749, 7750, 7751, 7752, 7753,
        7754, 7755
    },
    forest_troll_dragonsclaw = {
        444, 445, 446, 447, 448, 449, 1256, 1257, 1258, 6259,
        6260, 6261, 6262, 6961
    },
    cave_troll = {
        7707, 7712, 7713, 7714, 7715, 7716, 7717, 7718, 7719, 7720,
        7721, 7722, 7723, 7724, 7725, 7726, 7727, 7728, 7729, 7730,
        7731, 7732, 7733, 7734, 7735, 7736, 7737, 7738
    },
    fire_guardian = {
        7603, 7604, 7605, 7606, 7607, 7608, 7613, 7615, 7616, 7619,
        7632, 7633, 7634, 7637, 7638, 7639, 7640, 7641, 7642, 7643,
        7644, 7654, 7707, 7712, 7713
    },
    dark_shambler_beach = {
        7640, 7641, 7642, 7643, 7644, 7654, 7707, 7712, 7713, 7714,
        7715
    },
    sand_beetle = {
        7638, 7639, 7640, 7641, 7642, 7643, 7644, 7654
    },
}

return Spawns
