local Trouble = {}

Trouble.config = {
    city_name = "Ta'Vaalor",
    city_key = "tavaalor",
    zone_id = 2,
    min_players_online = 1,
    max_active_incidents = 1,
    incident_roll_interval_seconds = 360,
    incident_cooldown_seconds = 240,
    periodic_announcement_seconds = 180,
    min_participation_damage = 18,
    min_participation_kills = 1,
    min_reward_boxes = 1,
    max_reward_boxes = 5,
    average_level_floor = 3,
    average_level_ceiling = 60,
    resync_active_hostiles_seconds = 60,
    town_crier_name = "A town crier",
}

Trouble.cities = {
    tavaalor = {
        key = "tavaalor",
        zone_id = 2,
        display_name = "Ta'Vaalor",
        district_ids = {
            "victory_court",
            "annatto_gate",
            "garden_justice",
            "amaranth_dock",
        },
    },
}

Trouble.districts = {
    victory_court = {
        key = "victory_court",
        city_key = "tavaalor",
        label = "Victory Court",
        anchor_room_id = 3542,
        room_ids = { 3518, 3519, 3521, 3522, 3541, 3542 },
        scene_lines = {
            "A hard edge has settled over the court as runners and guards cut through the crowds.",
            "Citizens linger in doorways, watching the square with the taut silence of people waiting for trouble to break.",
        },
    },
    annatto_gate = {
        key = "annatto_gate",
        city_key = "tavaalor",
        label = "Annatto Gate",
        anchor_room_id = 3523,
        room_ids = { 3522, 3523, 3524, 5906, 10302 },
        scene_lines = {
            "The gate district thrums with anxious movement as guards search passersby and shout for witnesses.",
            "Crates stand half-split and abandoned near the roadway, suggesting someone fled in a hurry.",
        },
    },
    garden_justice = {
        key = "garden_justice",
        city_key = "tavaalor",
        label = "the Garden and Hall of Justice",
        anchor_room_id = 10374,
        room_ids = { 10373, 10374, 10375, 3540, 10382, 10383 },
        scene_lines = {
            "A cold, graveyard chill hangs over the district despite the city's usual order.",
            "Broken stone dust and dragged soil mark the paving as though something clawed its way up from below.",
        },
    },
    amaranth_dock = {
        key = "amaranth_dock",
        city_key = "tavaalor",
        label = "Amaranth Court and the river dock",
        anchor_room_id = 3486,
        room_ids = { 3485, 3486, 3487, 3488, 3492, 3493, 3494, 3495, 3544, 10381 },
        scene_lines = {
            "Raised voices and the sound of boots on stone carry through the district in ragged bursts.",
            "Watchful citizens hug the walls while nervous whispers ripple between the inn corner and the dock road.",
        },
    },
}

Trouble.hostile_variants = {
    contraband_runner = {
        key = "contraband_runner",
        base_template_id = "gnoll_thief",
        name = "contraband runner",
        article = "a",
        description = "Lean and quick, the runner keeps low under a patched cloak stuffed with illicit bundles and courier tags.",
        level_offset = 0,
        hp_mult = 0.95,
        as_mult = 1.00,
        ds_mult = 1.05,
        td_mult = 1.00,
        treasure = { coins = false, gems = false, magic = false, boxes = false },
    },
    dockside_brute = {
        key = "dockside_brute",
        base_template_id = "raider_orc",
        name = "dockside brute",
        article = "a",
        description = "Broad-shouldered and mean-eyed, the brute shoulders through the street with a cudgel and a willingness to use it.",
        level_offset = 1,
        hp_mult = 1.15,
        as_mult = 1.08,
        ds_mult = 0.96,
        td_mult = 1.00,
        treasure = { coins = false, gems = false, magic = false, boxes = false },
    },
    saboteur_enforcer = {
        key = "saboteur_enforcer",
        base_template_id = "rogue_hobgoblin_marauder",
        name = "saboteur enforcer",
        article = "a",
        description = "Soot-smudged hands and a belt full of tools mark the enforcer as someone sent to break things fast and disappear faster.",
        level_offset = 2,
        hp_mult = 1.10,
        as_mult = 1.10,
        ds_mult = 1.00,
        td_mult = 1.05,
        treasure = { coins = false, gems = false, magic = false, boxes = false },
    },
    catacomb_skeleton = {
        key = "catacomb_skeleton",
        base_template_id = "skeleton_warrior",
        name = "catacomb skeleton warrior",
        article = "a",
        description = "Still draped in age-darkened scraps of military regalia, the skeleton advances with a relentless martial precision.",
        level_offset = 0,
        hp_mult = 1.00,
        as_mult = 1.00,
        ds_mult = 1.00,
        td_mult = 1.00,
        treasure = { coins = false, gems = false, magic = false, boxes = false },
    },
    catacomb_ghoul = {
        key = "catacomb_ghoul",
        base_template_id = "ghoul",
        name = "catacomb ghoul",
        article = "a",
        description = "Rank earth clings to the ghoul's claws and lips, as though it only just hauled itself up from the crypts below.",
        level_offset = 1,
        hp_mult = 1.08,
        as_mult = 1.04,
        ds_mult = 0.98,
        td_mult = 1.00,
        treasure = { coins = false, gems = false, magic = false, boxes = false },
    },
    wight_captain = {
        key = "wight_captain",
        base_template_id = "arch_wight",
        name = "catacomb wight captain",
        article = "a",
        description = "A hateful, disciplined undead officer wrapped in old command finery and the cold of the grave.",
        level_offset = 3,
        hp_mult = 1.18,
        as_mult = 1.10,
        ds_mult = 1.08,
        td_mult = 1.15,
        treasure = { coins = false, gems = false, magic = false, boxes = false },
    },
}

Trouble.incidents = {
    annatto_smuggling_crackdown = {
        key = "annatto_smuggling_crackdown",
        city_key = "tavaalor",
        weight = 5,
        difficulty = 2,
        min_duration_seconds = 720,
        max_duration_seconds = 900,
        district_ids = { "annatto_gate", "amaranth_dock" },
        room_lines = {
            "A search line has formed through the district, and every loose crate seems one bad step from being kicked open.",
            "The sharp smell of split cedar and wet canvas suggests hidden cargo has just been uncovered nearby.",
        },
        crier_open = {
            "A town crier's voice rings across Ta'Vaalor, \"By order of the Legion, contraband runners have broken from %district%!  Citizens keep clear and report what you see!\"",
            "A town crier bellows through the streets, \"Smugglers are scattering through %district%!  Any able hand near the scene is called to assist the Legion!\"",
        },
        crier_progress = {
            "A town crier shouts, \"The chase through %district% is not yet done!  Legion hands still seek the last of the contraband ring!\"",
            "A town crier's warning carries on the air, \"The smuggler hunt in %district% continues.  Keep the streets clear for the responding patrols!\"",
        },
        crier_success = {
            "A town crier proclaims, \"The contraband ring in %district% has been broken.  Ta'Vaalor thanks those who answered the call!\"",
        },
        crier_fail = {
            "A town crier warns, \"The smugglers of %district% slipped the Legion's net.  Expect searches and stricter questioning through the quarter.\"",
        },
        stages = {
            {
                key = "first_break",
                label = "the first break from cover",
                spawn_room_ids = { 3522, 3523, 10302 },
                hostiles = {
                    { variant_id = "contraband_runner", count = 3 },
                    { variant_id = "dockside_brute", count = 1 },
                },
                completion_announcement = "A town crier shouts, \"The first wave in %district% has been checked, but the ring's handlers are still loose!\"",
            },
            {
                key = "handlers_cornered",
                label = "the handlers cornered",
                spawn_room_ids = { 3522, 3523, 5906 },
                hostiles = {
                    { variant_id = "contraband_runner", count = 2 },
                    { variant_id = "saboteur_enforcer", count = 1 },
                    { variant_id = "dockside_brute", count = 1 },
                },
                completion_announcement = "A town crier calls, \"The handlers in %district% are down!  Any surviving runners are being hunted through the ward!\"",
            },
        },
        rewards = {
            xp = 550,
            fame = 26,
            silver = 1200,
            box_min = 2,
            box_max = 4,
            box_level_bonus = 0,
        },
    },
    victory_saboteur_cell = {
        key = "victory_saboteur_cell",
        city_key = "tavaalor",
        weight = 4,
        difficulty = 3,
        min_duration_seconds = 780,
        max_duration_seconds = 1020,
        district_ids = { "victory_court" },
        room_lines = {
            "The court has taken on the brittle feel of a place one spark away from panic.",
            "Tools, broken lamp glass, and half-burned fuses lie underfoot where the saboteurs tried to make their work stick.",
        },
        crier_open = {
            "A town crier roars, \"Saboteurs have struck in %district%!  The Legion calls for immediate aid before the damage spreads!\"",
            "A town crier's warning crashes across the city, \"A coordinated cell is loose in %district%!  Anyone nearby with steel and sense, move!\"",
        },
        crier_progress = {
            "A town crier shouts, \"The saboteurs in %district% are bloodied but not broken.  Stay clear of the work crews and the damaged lanes!\"",
            "A town crier calls, \"The cell in %district% is still resisting.  Legion engineers remain under threat!\"",
        },
        crier_success = {
            "A town crier proclaims, \"The saboteur cell in %district% has been destroyed and the square secured.\"",
        },
        crier_fail = {
            "A town crier warns, \"The saboteurs in %district% escaped the square after causing damage enough to shame a watch captain.\"",
        },
        stages = {
            {
                key = "street_cutters",
                label = "the street cutters",
                spawn_room_ids = { 3518, 3519, 3541, 3542 },
                hostiles = {
                    { variant_id = "saboteur_enforcer", count = 2 },
                    { variant_id = "dockside_brute", count = 1 },
                },
                completion_announcement = "A town crier shouts, \"The square in %district% is holding, but the saboteur foreman is still at large!\"",
            },
            {
                key = "foreman_pushed_out",
                label = "the foreman pushed out",
                spawn_room_ids = { 3521, 3522, 3542 },
                hostiles = {
                    { variant_id = "saboteur_enforcer", count = 2 },
                    { variant_id = "contraband_runner", count = 1 },
                    { variant_id = "dockside_brute", count = 1 },
                },
                completion_announcement = "A town crier calls, \"The saboteur foreman in %district% has fallen.  Legion crews are moving to secure the damage!\"",
            },
        },
        rewards = {
            xp = 700,
            fame = 34,
            silver = 1800,
            box_min = 2,
            box_max = 5,
            box_level_bonus = 1,
        },
    },
    garden_catacomb_breach = {
        key = "garden_catacomb_breach",
        city_key = "tavaalor",
        weight = 3,
        difficulty = 4,
        min_duration_seconds = 900,
        max_duration_seconds = 1200,
        district_ids = { "garden_justice" },
        room_lines = {
            "The air in the district carries the wet, cold stink of opened crypts and disturbed grave soil.",
            "The city's calm has been replaced by the dreadful certainty that something dead is still moving nearby.",
        },
        crier_open = {
            "A town crier's voice cracks over the streets, \"A breach from the catacombs has fouled %district%!  Undead are above ground!  All capable hands respond!\"",
            "A town crier bellows, \"By order of the Hall of Justice, %district% is under grave breach.  The dead are walking the ward!\"",
        },
        crier_progress = {
            "A town crier shouts, \"The dead still push through %district%!  Priests and steel are needed before the breach worsens!\"",
            "A town crier warns, \"The catacomb breach beneath %district% is not sealed.  Keep clear unless you mean to fight!\"",
        },
        crier_success = {
            "A town crier proclaims, \"The catacomb breach in %district% has been beaten back beneath the stones.\"",
        },
        crier_fail = {
            "A town crier warns, \"The dead were not fully put down in %district%.  The Hall of Justice has ordered the ward sealed and searched.\"",
        },
        stages = {
            {
                key = "bone_push",
                label = "the bone push",
                spawn_room_ids = { 10373, 10374, 10375 },
                hostiles = {
                    { variant_id = "catacomb_skeleton", count = 3 },
                    { variant_id = "catacomb_ghoul", count = 1 },
                },
                completion_announcement = "A town crier shouts, \"The first dead in %district% are down, but the deeper rot is still climbing!\"",
            },
            {
                key = "grave_wave",
                label = "the grave wave",
                spawn_room_ids = { 3540, 10382, 10383 },
                hostiles = {
                    { variant_id = "catacomb_skeleton", count = 2 },
                    { variant_id = "catacomb_ghoul", count = 2 },
                },
                completion_announcement = "A town crier calls, \"The breach in %district% is narrowing, but a grave captain still commands what remains!\"",
            },
            {
                key = "wight_captain",
                label = "the grave captain",
                spawn_room_ids = { 10374, 10382 },
                hostiles = {
                    { variant_id = "wight_captain", count = 1 },
                    { variant_id = "catacomb_ghoul", count = 1 },
                },
                completion_announcement = "A town crier cries, \"The grave captain in %district% has fallen!  Priests are moving now to seal the breach!\"",
            },
        },
        rewards = {
            xp = 950,
            fame = 46,
            silver = 2600,
            box_min = 3,
            box_max = 5,
            box_level_bonus = 2,
        },
    },
    dockside_breakout = {
        key = "dockside_breakout",
        city_key = "tavaalor",
        weight = 4,
        difficulty = 2,
        min_duration_seconds = 660,
        max_duration_seconds = 840,
        district_ids = { "amaranth_dock" },
        room_lines = {
            "The river quarter is alive with shouted warnings and the slap of hurried boots against wet stone.",
            "Whatever burst out toward the dock left torn netting, broken crates, and an ugly trail of panic behind it.",
        },
        crier_open = {
            "A town crier bellows, \"A violent breakout is tearing through %district%!  The dock quarter needs immediate hands!\"",
            "A town crier calls through Ta'Vaalor, \"The river quarter in %district% is in uproar.  Any adventurer nearby is ordered to assist!\"",
        },
        crier_progress = {
            "A town crier shouts, \"The trouble in %district% still runs hot.  Keep the road to the dock clear!\"",
            "A town crier warns, \"The breakout in %district% is not yet contained.  Keep citizens away from the river approach!\"",
        },
        crier_success = {
            "A town crier proclaims, \"The dockside breakout in %district% has been put down and the ward secured.\"",
        },
        crier_fail = {
            "A town crier warns, \"The breakout in %district% scattered into the dark and left the river ward reeling.\"",
        },
        stages = {
            {
                key = "quarter_surge",
                label = "the first surge",
                spawn_room_ids = { 3485, 3486, 3493, 3494 },
                hostiles = {
                    { variant_id = "contraband_runner", count = 2 },
                    { variant_id = "dockside_brute", count = 2 },
                },
                completion_announcement = "A town crier cries, \"The first rush in %district% has been checked, but the river road is not clear yet!\"",
            },
            {
                key = "dock_holdouts",
                label = "the dock holdouts",
                spawn_room_ids = { 3544, 10381, 3495 },
                hostiles = {
                    { variant_id = "dockside_brute", count = 2 },
                    { variant_id = "saboteur_enforcer", count = 1 },
                },
                completion_announcement = "A town crier calls, \"The dock holdouts in %district% have been crushed.  The quarter is settling again!\"",
            },
        },
        rewards = {
            xp = 600,
            fame = 28,
            silver = 1400,
            box_min = 2,
            box_max = 4,
            box_level_bonus = 0,
        },
    },
}

return Trouble
