---------------------------------------------------
-- Solhaven / Vornavis Coast — Spawn Registry
-- scripts/zones/solhaven/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "solhaven"
Spawns.area       = "Solhaven / Vornavis Coast"
Spawns.room_range = { min = 151, max = 7755 }

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

return Spawns
