---------------------------------------------------
-- Wehnimer's Landing — Spawn Registry
-- Catacombs, Sewers, Kobold Mines, Mine Road,
-- Graveyard, Upper Trollfang
---------------------------------------------------

local Spawns = {}

Spawns.zone = "wehnimers_landing"

Spawns.population = {
    -- ── Catacombs / Sewers ────────────────────────────────────────────────
    { mob = "giant_rat",          level = 1,  max = 14, depth = "sewers_upper" },
    { mob = "giant_ant",          level = 1,  max = 12, depth = "ant_nest" },
    { mob = "thyril_catacombs",   level = 2,  max = 8,  depth = "catacomb_upper" },
    { mob = "cave_gnome",         level = 2,  max = 8,  depth = "catacomb_mid" },
    { mob = "relnak",             level = 3,  max = 7,  depth = "catacomb_mid" },
    { mob = "fire_salamander",    level = 3,  max = 6,  depth = "catacomb_deep" },
    -- ── Kobold Mines ──────────────────────────────────────────────────────
    { mob = "big_ugly_kobold",    level = 2,  max = 8,  depth = "kobold_mines" },
    { mob = "kobold_shepherd",    level = 3,  max = 5,  depth = "kobold_mines_deep" },
    -- ── Mine Road / Old Mine ──────────────────────────────────────────────
    { mob = "mountain_rolton",    level = 1,  max = 10, depth = "mine_road" },
    { mob = "cave_nipper",        level = 3,  max = 7,  depth = "abandoned_mine" },
    { mob = "cave_worm",          level = 10, max = 3,  depth = "mine_road" },
    { mob = "crystal_golem",      level = 12, max = 3,  depth = "mine_road_deep" },
    -- ── Graveyard ─────────────────────────────────────────────────────────
    { mob = "lesser_shade",       level = 2,  max = 10, depth = "graveyard" },
    { mob = "phantom",            level = 2,  max = 6,  depth = "graveyard" },
    { mob = "hobgoblin",          level = 3,  max = 7,  depth = "graveyard" },
    { mob = "cobra",              level = 4,  max = 6,  depth = "graveyard" },
    { mob = "lesser_mummy",       level = 6,  max = 5,  depth = "graveyard" },
    { mob = "albino_tomb_spider", level = 8,  max = 5,  depth = "graveyard" },
    -- ── Upper Trollfang entry (level 2-5) ─────────────────────────────────
    { mob = "goblin",             level = 2,  max = 10, depth = "trollfang_upper" },
    { mob = "spotted_gak",        level = 2,  max = 8,  depth = "trollfang_upper" },
    { mob = "cave_gnoll",         level = 3,  max = 6,  depth = "trollfang_upper" },
    { mob = "striped_gak",        level = 3,  max = 7,  depth = "trollfang_upper" },
    { mob = "troglodyte",         level = 3,  max = 6,  depth = "trollfang_upper" },
    { mob = "velnalin",           level = 3,  max = 7,  depth = "trollfang_upper" },
    { mob = "mountain_snowcat",   level = 3,  max = 5,  depth = "trollfang_upper" },
    { mob = "ridge_orc",          level = 4,  max = 7,  depth = "trollfang_upper" },
    { mob = "mongrel_hobgoblin",  level = 5,  max = 7,  depth = "trollfang_upper" },
    -- ── Upper Trollfang deeper (level 5-18) ───────────────────────────────
    { mob = "coyote_trollfang",   level = 5,  max = 6,  depth = "trollfang_upper" },
    { mob = "lesser_orc",         level = 6,  max = 8,  depth = "trollfang_upper" },
    { mob = "cockatrice",         level = 6,  max = 4,  depth = "trollfang_bridge" },
    { mob = "hobgoblin_shaman",   level = 7,  max = 4,  depth = "trollfang_upper" },
    { mob = "greater_orc",        level = 8,  max = 6,  depth = "trollfang_swamp" },
    { mob = "werebear",           level = 10, max = 2,  depth = "secluded_valley" },
    { mob = "gnoll_worker",       level = 10, max = 6,  depth = "mountain_foothills" },
    { mob = "darkwoode",          level = 13, max = 4,  depth = "sentoph" },
    { mob = "gnoil_thief",        level = 13, max = 5,  depth = "imaera_path" },
    { mob = "forest_troll",       level = 14, max = 4,  depth = "trollfang_swamp" },
    { mob = "grey_orc_trollfang", level = 14, max = 5,  depth = "trollfang_lower" },
    { mob = "gnoll_ranger",       level = 15, max = 4,  depth = "imaera_path" },
    { mob = "wolfshade",          level = 15, max = 3,  depth = "twisted_trail" },
    { mob = "dark_shambler",      level = 17, max = 4,  depth = "sentoph" },
    { mob = "nedum_vereri",       level = 18, max = 2,  depth = "temple_of_love" },
    -- ── High-level ────────────────────────────────────────────────────────
    { mob = "skeletal_giant",     level = 33, max = 2,  depth = "obsidian_tower" },
    { mob = "storm_giant",        level = 39, max = 1,  depth = "sentoph_deep" },
}

return Spawns
