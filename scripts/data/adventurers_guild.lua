---------------------------------------------------
-- data/adventurers_guild.lua
-- Shared Adventurer's Guild registration, rank,
-- and bounty contract definitions.
---------------------------------------------------

local AG = {}

AG.rank_thresholds = {
    { points = 0,  rank = 1, title = "Associate" },
    { points = 5,  rank = 2, title = "Junior Adventurer" },
    { points = 12, rank = 3, title = "Field Adventurer" },
    { points = 22, rank = 4, title = "Senior Adventurer" },
    { points = 36, rank = 5, title = "Guild Pathfinder" },
    { points = 55, rank = 6, title = "Guild Champion" },
}

AG.authorities = {
    halline = {
        template_id = "halline",
        town_name = "Icemule Trace",
        room_id = 3779,
        role = "taskmaster",
    },
    rheteger = {
        template_id = "rheteger",
        town_name = "Wehnimer's Landing",
        room_id = 3785,
        role = "taskmaster",
    },
    torsidr = {
        template_id = "torsidr",
        town_name = "Ta'Vaalor",
        room_id = 10332,
        role = "taskmaster",
    },
    guild_clerk = {
        template_id = "guild_clerk",
        town_name = "Ta'Vaalor",
        room_id = 10331,
        role = "clerk",
    },
}

AG.towns = {
    ["Wehnimer's Landing"] = {
        taskmaster = "rheteger",
        taskmaster_room_id = 3785,
        clerk = nil,
        clerk_room_id = nil,
        bounty_room_ids = { 3785 },
    },
    ["Icemule Trace"] = {
        taskmaster = "halline",
        taskmaster_room_id = 3779,
        clerk = nil,
        clerk_room_id = nil,
        bounty_room_ids = { 3779 },
    },
    ["Ta'Vaalor"] = {
        taskmaster = "torsidr",
        taskmaster_room_id = 10332,
        clerk = "guild_clerk",
        clerk_room_id = 10331,
        bounty_room_ids = { 10331, 10332 },
    },
}

AG.bounties = {
    ["Wehnimer's Landing"] = {
        { key = "wl_giant_rat",      type = "cull", min_level = 1,  max_level = 2,  target_template_id = "giant_rat",        target_name = "giant rat",        target_count = 8, reward_silver = 250, reward_experience = 120, reward_fame = 8,  reward_points = 1, area = "the catacombs beneath the Landing" },
        { key = "wl_giant_ant",      type = "cull", min_level = 1,  max_level = 3,  target_template_id = "giant_ant",        target_name = "giant ant",        target_count = 8, reward_silver = 275, reward_experience = 135, reward_fame = 9,  reward_points = 1, area = "the catacombs beneath the Landing" },
        { key = "wl_cave_gnome",     type = "cull", min_level = 3,  max_level = 5,  target_template_id = "cave_gnome",       target_name = "cave gnome",       target_count = 6, reward_silver = 360, reward_experience = 180, reward_fame = 12, reward_points = 1, area = "the Landing's deeper tunnels" },
        { key = "wl_relnak",         type = "cull", min_level = 4,  max_level = 7,  target_template_id = "relnak",           target_name = "relnak",           target_count = 6, reward_silver = 420, reward_experience = 210, reward_fame = 14, reward_points = 2, area = "the Landing catacombs" },
        { key = "wl_fire_salamander",type = "cull", min_level = 6,  max_level = 10, target_template_id = "fire_salamander",  target_name = "fire salamander",  target_count = 5, reward_silver = 560, reward_experience = 260, reward_fame = 18, reward_points = 2, area = "the steaming catacomb tunnels" },
        { key = "wl_lesser_shade",   type = "cull", min_level = 8,  max_level = 12, target_template_id = "lesser_shade",     target_name = "lesser shade",     target_count = 5, reward_silver = 700, reward_experience = 320, reward_fame = 22, reward_points = 3, area = "the haunted tunnels" },
        { key = "wl_hobgoblin",      type = "cull", min_level = 10, max_level = 15, target_template_id = "hobgoblin",        target_name = "hobgoblin",        target_count = 6, reward_silver = 850, reward_experience = 390, reward_fame = 26, reward_points = 3, area = "the Trollfang outskirts" },
        { key = "wl_lesser_orc",     type = "cull", min_level = 13, max_level = 20, target_template_id = "lesser_orc",       target_name = "lesser orc",       target_count = 6, reward_silver = 1050, reward_experience = 450, reward_fame = 30, reward_points = 4, area = "the rough country beyond the Landing" },
        { key = "wl_gem_packet",     type = "gem", min_level = 1, max_level = 10, target_name = "uncut gems", target_count = 3, reward_silver = 310, reward_experience = 150, reward_fame = 10, reward_points = 1, area = "the Landing catacombs and nearby wilds", target_item_type = "gem" },
        { key = "wl_skin_bundle",    type = "skin", min_level = 2, max_level = 12, target_name = "fresh skins", target_count = 3, reward_silver = 350, reward_experience = 170, reward_fame = 11, reward_points = 1, area = "the wild country near the Landing", target_item_type = "skin" },
        { key = "wl_herb_bundle",    type = "forage", min_level = 3, max_level = 12, target_name = "field herbs", target_count = 3, reward_silver = 390, reward_experience = 190, reward_fame = 12, reward_points = 2, area = "the countryside around Wehnimer's Landing", target_item_type = "herb" },
        { key = "wl_heirloom_search",type = "heirloom", min_level = 4, max_level = 14, target_name = "lost signet ring", target_count = 1, reward_silver = 520, reward_experience = 240, reward_fame = 16, reward_points = 2, area = "the catacombs beneath the Landing", found_item_name = "a tarnished signet ring", found_item_short_name = "tarnished signet ring", found_item_noun = "ring", search_zone_names = { "the catacombs" }, search_room_ids = { 3933, 3934, 3935, 3936, 3937, 404 } },
        { key = "wl_bandit_hobgoblin", type = "bandit", min_level = 6, max_level = 15, target_template_id = "hobgoblin", target_name = "rogue hobgoblin marauder", target_count = 4, reward_silver = 780, reward_experience = 345, reward_fame = 24, reward_points = 3, area = "the rough country around the Landing" },
        { key = "wl_boss_orc",       type = "boss", min_level = 10, max_level = 20, target_template_id = "lesser_orc", target_name = "lesser orc warleader", target_count = 1, reward_silver = 1180, reward_experience = 520, reward_fame = 34, reward_points = 4, area = "the rough country beyond the Landing" },
        { key = "wl_escort_moot_hall", type = "escort", min_level = 1, max_level = 12, target_name = "a sealed guild dispatch", target_count = 2, reward_silver = 360, reward_experience = 165, reward_fame = 11, reward_points = 1, area = "between the Adventurer's Guild and Moot Hall", destination_room_id = 7970, destination_name = "Moot Hall", report_room_id = 3785 },
        { key = "wl_rescue_catacombs", type = "rescue", min_level = 3, max_level = 14, target_name = "a missing tunnel runner", target_count = 2, reward_silver = 560, reward_experience = 250, reward_fame = 17, reward_points = 2, area = "the catacombs beneath the Landing", search_zone_names = { "the catacombs" }, search_room_ids = { 3933, 3934, 3935, 3936, 3937, 404 }, report_room_id = 3785 },
    },
    ["Icemule Trace"] = {
        { key = "imt_carrion_worm",  type = "cull", min_level = 1,  max_level = 2,  target_template_id = "carrion_worm",     target_name = "carrion worm",     target_count = 8, reward_silver = 250, reward_experience = 120, reward_fame = 8,  reward_points = 1, area = "the environs near Icemule" },
        { key = "imt_kobold",        type = "cull", min_level = 1,  max_level = 3,  target_template_id = "kobold_imt",       target_name = "kobold",           target_count = 8, reward_silver = 275, reward_experience = 135, reward_fame = 9,  reward_points = 1, area = "the environs near Icemule" },
        { key = "imt_rolton",        type = "cull", min_level = 2,  max_level = 4,  target_template_id = "rolton",           target_name = "rolton",           target_count = 7, reward_silver = 320, reward_experience = 155, reward_fame = 10, reward_points = 1, area = "the snowfields outside town" },
        { key = "imt_leaper",        type = "cull", min_level = 3,  max_level = 6,  target_template_id = "leaper",           target_name = "leaper",           target_count = 6, reward_silver = 390, reward_experience = 190, reward_fame = 13, reward_points = 2, area = "the woodline and snow trails" },
        { key = "imt_white_vysan",   type = "cull", min_level = 5,  max_level = 9,  target_template_id = "white_vysan",      target_name = "white vysan",      target_count = 6, reward_silver = 500, reward_experience = 240, reward_fame = 16, reward_points = 2, area = "the frozen uplands" },
        { key = "imt_lesser_frost_shade", type = "cull", min_level = 7,  max_level = 12, target_template_id = "lesser_frost_shade", target_name = "lesser frost shade", target_count = 5, reward_silver = 650, reward_experience = 300, reward_fame = 20, reward_points = 3, area = "the colder caves and drifts" },
        { key = "imt_ice_hound",     type = "cull", min_level = 9,  max_level = 15, target_template_id = "ice_hound",        target_name = "ice hound",        target_count = 5, reward_silver = 820, reward_experience = 365, reward_fame = 24, reward_points = 3, area = "the harder trails beyond Icemule" },
        { key = "imt_lesser_orc",    type = "cull", min_level = 12, max_level = 20, target_template_id = "lesser_orc_imt",   target_name = "lesser orc",       target_count = 6, reward_silver = 1000, reward_experience = 440, reward_fame = 29, reward_points = 4, area = "the rough country north of town" },
        { key = "imt_gem_packet",    type = "gem", min_level = 1, max_level = 10, target_name = "winter-found gems", target_count = 3, reward_silver = 320, reward_experience = 155, reward_fame = 10, reward_points = 1, area = "the snowy reaches beyond Icemule", target_item_type = "gem" },
        { key = "imt_skin_bundle",   type = "skin", min_level = 2, max_level = 14, target_name = "winter pelts", target_count = 3, reward_silver = 370, reward_experience = 180, reward_fame = 12, reward_points = 1, area = "the surrounding snowfields", target_item_type = "skin" },
        { key = "imt_herb_bundle",   type = "forage", min_level = 3, max_level = 14, target_name = "healing herbs", target_count = 3, reward_silver = 410, reward_experience = 205, reward_fame = 13, reward_points = 2, area = "the icy woodline and drifts", target_item_type = "herb" },
        { key = "imt_heirloom_search", type = "heirloom", min_level = 5, max_level = 15, target_name = "missing courier satchel", target_count = 1, reward_silver = 560, reward_experience = 255, reward_fame = 17, reward_points = 2, area = "the southern snowfields", found_item_name = "a weather-beaten courier satchel", found_item_short_name = "weather-beaten courier satchel", found_item_noun = "satchel", search_zone_names = { "the southern snowfields" } },
        { key = "imt_bandit_orc",    type = "bandit", min_level = 8, max_level = 18, target_template_id = "lesser_orc_imt", target_name = "lesser orc raider", target_count = 4, reward_silver = 830, reward_experience = 370, reward_fame = 25, reward_points = 3, area = "the rough country north of Icemule" },
        { key = "imt_boss_hound",    type = "boss", min_level = 9, max_level = 20, target_template_id = "ice_hound", target_name = "ice hound pack leader", target_count = 1, reward_silver = 1230, reward_experience = 540, reward_fame = 35, reward_points = 4, area = "the harder trails beyond Icemule" },
        { key = "imt_escort_bondsman", type = "escort", min_level = 1, max_level = 12, target_name = "a guild dispatch case", target_count = 2, reward_silver = 370, reward_experience = 170, reward_fame = 11, reward_points = 1, area = "between the guild office and the bondsman's counter", destination_room_id = 2438, destination_name = "the bondsman's counter", report_room_id = 3779 },
        { key = "imt_rescue_snowfield", type = "rescue", min_level = 4, max_level = 16, target_name = "a missing snow-runner", target_count = 2, reward_silver = 590, reward_experience = 265, reward_fame = 18, reward_points = 2, area = "the southern snowfields", search_zone_names = { "the southern snowfields" }, report_room_id = 3779 },
    },
    ["Ta'Vaalor"] = {
        { key = "tv_fanged_rodent",  type = "cull", min_level = 1,  max_level = 2,  target_template_id = "fanged_rodent",    target_name = "fanged rodent",    target_count = 8, reward_silver = 250, reward_experience = 120, reward_fame = 8,  reward_points = 1, area = "the Ta'Vaalor catacombs" },
        { key = "tv_catacomb_rat",   type = "cull", min_level = 1,  max_level = 3,  target_template_id = "catacomb_rat",     target_name = "catacomb rat",     target_count = 8, reward_silver = 275, reward_experience = 135, reward_fame = 9,  reward_points = 1, area = "the Ta'Vaalor catacombs" },
        { key = "tv_young_grass_snake", type = "cull", min_level = 2, max_level = 4, target_template_id = "young_grass_snake", target_name = "young grass snake", target_count = 7, reward_silver = 320, reward_experience = 155, reward_fame = 10, reward_points = 1, area = "the Rambling Meadows" },
        { key = "tv_thyril",         type = "cull", min_level = 3,  max_level = 6,  target_template_id = "thyril_meadows",   target_name = "thyril",           target_count = 6, reward_silver = 380, reward_experience = 185, reward_fame = 12, reward_points = 2, area = "the meadows beyond the gates" },
        { key = "tv_striped_relnak", type = "cull", min_level = 4,  max_level = 8,  target_template_id = "striped_relnak",   target_name = "striped relnak",   target_count = 6, reward_silver = 460, reward_experience = 220, reward_fame = 15, reward_points = 2, area = "the Rambling Meadows" },
        { key = "tv_spotted_leaper", type = "cull", min_level = 5,  max_level = 10, target_template_id = "spotted_leaper",   target_name = "spotted leaper",   target_count = 6, reward_silver = 560, reward_experience = 260, reward_fame = 18, reward_points = 2, area = "the meadows and roadways outside Ta'Vaalor" },
        { key = "tv_neartofar_orc",  type = "cull", min_level = 9,  max_level = 15, target_template_id = "neartofar_orc",    target_name = "neartofar orc",    target_count = 5, reward_silver = 760, reward_experience = 340, reward_fame = 23, reward_points = 3, area = "Neartofar Forest" },
        { key = "tv_neartofar_troll",type = "cull", min_level = 12, max_level = 20, target_template_id = "neartofar_troll",  target_name = "neartofar troll",  target_count = 5, reward_silver = 980, reward_experience = 430, reward_fame = 29, reward_points = 4, area = "Neartofar Forest" },
        { key = "tv_gem_packet",     type = "gem", min_level = 1, max_level = 12, target_name = "salvaged stones", target_count = 3, reward_silver = 330, reward_experience = 160, reward_fame = 10, reward_points = 1, area = "the outskirts of Ta'Vaalor", target_item_type = "gem" },
        { key = "tv_skin_bundle",    type = "skin", min_level = 2, max_level = 14, target_name = "usable pelts and hides", target_count = 3, reward_silver = 390, reward_experience = 185, reward_fame = 12, reward_points = 1, area = "the meadows and forest roads", target_item_type = "skin" },
        { key = "tv_herb_bundle",    type = "forage", min_level = 3, max_level = 14, target_name = "field herbs", target_count = 3, reward_silver = 430, reward_experience = 210, reward_fame = 13, reward_points = 2, area = "the roads and meadows outside the city", target_item_type = "herb" },
        { key = "tv_heirloom_search",type = "heirloom", min_level = 4, max_level = 16, target_name = "missing legion signet", target_count = 1, reward_silver = 590, reward_experience = 275, reward_fame = 18, reward_points = 2, area = "the roads beyond the Victory and Vermilion Gates", found_item_name = "a mud-streaked legion signet", found_item_short_name = "mud-streaked legion signet", found_item_noun = "signet", search_zone_names = { "Timmorain Road", "the Rambling Meadows", "the Neartofar Road" }, search_room_ids = { 5830, 5831, 5833, 5950, 5951, 5952 } },
        { key = "tv_bandit_raider",  type = "bandit", min_level = 8, max_level = 18, target_template_id = "raider_orc", target_name = "raider orc marauder", target_count = 4, reward_silver = 860, reward_experience = 390, reward_fame = 26, reward_points = 3, area = "the roads and farms outside Ta'Vaalor" },
        { key = "tv_boss_troll",     type = "boss", min_level = 12, max_level = 20, target_template_id = "neartofar_troll", target_name = "neartofar troll champion", target_count = 1, reward_silver = 1280, reward_experience = 560, reward_fame = 36, reward_points = 4, area = "Neartofar Forest" },
        { key = "tv_escort_clerk",   type = "escort", min_level = 1, max_level = 12, target_name = "a stack of sealed contracts", target_count = 2, reward_silver = 390, reward_experience = 180, reward_fame = 12, reward_points = 1, area = "between the taskmaster and the guild clerk", destination_room_id = 10331, destination_name = "the guild clerk's foyer", report_room_id = 10332 },
        { key = "tv_rescue_road",    type = "rescue", min_level = 4, max_level = 16, target_name = "a missing legion runner", target_count = 2, reward_silver = 620, reward_experience = 280, reward_fame = 19, reward_points = 2, area = "the roads beyond the city gates", search_zone_names = { "Timmorain Road", "the Rambling Meadows", "the Neartofar Road" }, search_room_ids = { 5830, 5831, 5833, 5950, 5951, 5952 }, report_room_id = 10332 },
    },
}

return AG
