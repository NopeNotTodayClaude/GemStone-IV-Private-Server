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
    },
}

return AG
