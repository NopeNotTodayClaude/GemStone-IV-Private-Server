local Inns = {}

-- Inn registry anchored to local room IDs.
-- Data here is intentionally explicit only where the room graph is not
-- discoverable from the room titles alone.  The runtime expands each inn's
-- footprint by matching title prefixes and location names against loaded rooms.

Inns.defaults = {
    auto_latch_tag = true,
}

Inns.inns = {
    friths_inn = {
        display_name = "Frith's Inn",
        town_name = "Wehnimer's Landing",
        front_desk_room_id = 1264,
        aliases = { "friths", "frith", "wehnimer", "landing", "wl" },
        room_title_prefixes = { "Frith's Inn" },
        explicit_room_ids = { 1262, 1263, 1264, 8812, 8813, 8814, 8815, 8816 },
        rentable_room_ids = { 8813, 8814, 8815 },
        private_table_room_ids = { 8816 },
        innkeeper_template_ids = { "wl_frith_innkeeper" },
    },

    raging_thrak = {
        display_name = "Raging Thrak Inn",
        town_name = "Wehnimer's Landing",
        front_desk_room_id = 8671,
        aliases = { "raging thrak", "thrak", "wehnimer", "landing", "wl" },
        room_title_prefixes = { "Raging Thrak Inn" },
        explicit_room_ids = { 1194, 8671, 8672, 8673, 8675 },
        rentable_room_ids = { 8673 },
    },

    thirsty_penguin = {
        display_name = "Thirsty Penguin",
        town_name = "Icemule Trace",
        front_desk_room_id = 3427,
        aliases = { "thirsty penguin", "penguin", "icemule", "imt", "mule" },
        room_title_prefixes = { "Thirsty Penguin" },
        explicit_room_ids = { 3427, 3428, 15801, 15802, 15803 },
        rentable_room_ids = { 15802, 15803 },
        innkeeper_template_ids = { "imt_inn_keeper_imt" },
    },

    shimmarglin_inn = {
        display_name = "Shimmarglin Inn",
        town_name = "Shimmarglin",
        front_desk_room_id = 597,
        aliases = { "shimmarglin", "shimmarglin inn" },
        room_title_prefixes = { "Shimmarglin Inn" },
        explicit_room_ids = { 596, 597, 599, 601 },
    },

    golden_helm = {
        display_name = "Golden Helm",
        town_name = "Kharam-Dzu",
        front_desk_room_id = 1842,
        aliases = { "golden helm", "kharam dzu", "kd", "teras" },
        room_title_prefixes = { "Golden Helm" },
        explicit_room_ids = { 1842, 12506, 12508, 12509, 12510 },
        rentable_room_ids = { 12508, 12509, 12510 },
        innkeeper_template_ids = { "ti_inn_keeper_ti" },
    },

    solhaven_inn = {
        display_name = "Solhaven Inn",
        town_name = "Solhaven",
        front_desk_room_id = 5714,
        aliases = { "solhaven inn", "solhaven", "sol" },
        room_title_prefixes = { "Solhaven Inn" },
        explicit_room_ids = { 5714, 5715, 5716, 13243, 13492, 13498, 17166, 17172, 17174, 17175, 17176 },
        rentable_room_ids = { 13492, 13498, 17166, 17172, 17174, 17175, 17176 },
        innkeeper_template_ids = { "sol_inn_keeper_sol" },
    },

    feystone_inn = {
        display_name = "The Feystone Inn",
        town_name = "Ta'Illistim",
        front_desk_room_id = 9921,
        aliases = { "feystone", "feystone inn", "ta'illistim", "taillistim", "ti" },
        room_title_prefixes = { "The Feystone Inn" },
        explicit_room_ids = { 9920, 9921, 9923, 9924, 15608 },
        rentable_room_ids = { 9924 },
        innkeeper_template_ids = { "tai_inn_keeper_tai" },
    },

    rivers_rest_inn = {
        display_name = "River's Rest Inn",
        town_name = "River's Rest",
        front_desk_room_id = 10956,
        aliases = { "river's rest", "rivers rest", "rest", "rr" },
        room_title_prefixes = { "River's Rest Inn" },
        explicit_room_ids = { 10956, 10957, 10958, 10960, 10962, 10963, 10964, 10965, 17081, 17983 },
        rentable_room_ids = { 10962, 10964, 10965 },
        innkeeper_template_ids = { "rr_inn_keeper_rr" },
    },

    bawdy_bard = {
        display_name = "Bawdy Bard Inn",
        town_name = "Zul Logoth",
        front_desk_room_id = 9482,
        aliases = { "bawdy bard", "bawdy bard inn", "zul logoth", "zul", "zl" },
        room_title_prefixes = { "Bawdy Bard Inn" },
        explicit_room_ids = { 9481, 9482, 16849 },
        innkeeper_template_ids = { "zl_inn_keeper_zl" },
    },

    legendary_rest = {
        display_name = "The Legendary Rest",
        town_name = "The Legendary Rest",
        front_desk_room_id = 5826,
        aliases = { "legendary rest", "rest" },
        room_title_prefixes = { "The Legendary Rest" },
        explicit_room_ids = { 5825, 5826 },
    },

    sea_hags_roost = {
        display_name = "The Sea Hag's Roost",
        town_name = "Kraken's Fall",
        front_desk_room_id = 28947,
        aliases = { "sea hag", "sea hags roost", "roost", "kraken", "kraken's fall", "kf" },
        room_title_prefixes = { "The Sea Hag's Roost" },
        explicit_room_ids = { 28947, 28950, 29102, 29103 },
        rentable_room_ids = { 29102, 29103 },
        innkeeper_template_ids = { "kf_inn_keeper_kf" },
    },

    moonglae_inn = {
        display_name = "Moonglae Inn",
        town_name = "Moonglae Inn",
        front_desk_room_id = 6,
        aliases = { "moonglae", "moonglae inn" },
        room_title_prefixes = { "Moonglae Inn" },
        location_names = { "the Moonglae Inn" },
        explicit_room_ids = {
            5, 6, 13303, 13304, 13305, 13353, 13354, 13355, 13356, 13357,
            13358, 15652, 15653, 26042, 26043, 32742, 32743, 32744, 32745,
            32746, 32747, 32748, 32749, 32750, 32751, 32752, 32753
        },
        rentable_room_ids = { 13304, 13356, 13357, 32747, 32748, 32749, 32750, 32751, 32752, 32753 },
        private_table_room_ids = { 1, 2, 3, 147, 148, 202, 595, 631, 632, 633, 687, 688, 689, 27048, 27049 },
    },

    naerine_hostelry = {
        display_name = "Naerine Hostelry",
        town_name = "Cysaegir",
        front_desk_room_id = 4689,
        aliases = { "naerine", "naerine hostelry", "cysaegir", "cysa" },
        room_title_prefixes = { "Naerine Hostelry" },
        explicit_room_ids = { 4687, 4688, 4689 },
    },

    malwith_inn = {
        display_name = "Malwith Inn",
        town_name = "Ta'Vaalor",
        front_desk_room_id = 10385,
        aliases = { "malwith", "malwith inn", "ta'vaalor", "tavaalor", "vaalor", "tv" },
        room_title_prefixes = { "Malwith Inn" },
        explicit_room_ids = {
            10384, 10385, 10386, 10387, 10388, 10389, 10390, 10391, 10392, 10393,
            13312, 13699, 13700, 13701, 13704, 13705, 15563, 17323, 17324, 17325,
            21223, 28283, 30499
        },
        rentable_room_ids = { 13705, 15563, 17323, 17325 },
        private_table_room_ids = { 28283 },
        innkeeper_template_ids = { "tv_malwith_innkeeper" },
    },

    firefly_villa = {
        display_name = "Firefly Villa",
        town_name = "Mist Harbor",
        front_desk_room_id = 16411,
        aliases = { "firefly villa", "firefly", "mist harbor", "mistharbor" },
        room_title_prefixes = { "Firefly Villa" },
        explicit_room_ids = { 12331, 16411 },
    },

    harbors_echo = {
        display_name = "Harbor's Echo Inn",
        town_name = "Isle of Ornath",
        front_desk_room_id = 35346,
        aliases = { "harbor's echo", "harbors echo", "ornath" },
        room_title_prefixes = { "Harbor's Echo Inn" },
        explicit_room_ids = { 35346 },
    },
}

return Inns
