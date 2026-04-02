local Justice = {}

Justice.config = {
    answer_timeout_sec = 120,
    jail_question_interval_sec = 120,
    missed_answer_penalty_sec = 180,
    wrong_answer_penalty_sec = 120,
    contempt_penalty_sec = 300,
    fine_due_sec = 1260,
    service_step_credit_sec = 90,
    arrest_roundtime_sec = 3,
    sentence_roundtime_sec = 2,
    accusation_window_sec = 900,
    history_retention_days = 180,
}

Justice.charge_defs = {
    impropriety = {
        label = "Impropriety",
        accusable = true,
        severity = 1,
        fine = 500,
        incarceration_min = 5,
        service_min = 5,
        allow_service = true,
    },
    hooliganism = {
        label = "Hooliganism",
        accusable = true,
        severity = 1,
        fine = 900,
        incarceration_min = 8,
        service_min = 8,
        allow_service = true,
    },
    assault = {
        label = "Assault",
        accusable = true,
        severity = 2,
        fine = 1800,
        incarceration_min = 12,
        service_min = 12,
        allow_service = true,
    },
    theft = {
        label = "Theft",
        accusable = true,
        severity = 2,
        fine = 2500,
        incarceration_min = 15,
        service_min = 15,
        allow_service = true,
    },
    banishment = {
        label = "Banishment",
        accusable = true,
        severity = 4,
        fine = 10000,
        incarceration_min = 35,
        service_min = 0,
        allow_service = false,
        banishment_days = 14,
    },
    endangering_public_safety = {
        label = "Endangering Public Safety",
        severity = 3,
        fine = 4800,
        incarceration_min = 20,
        service_min = 20,
        allow_service = true,
    },
    disturbing_the_peace = {
        label = "Disturbing the Peace",
        severity = 2,
        fine = 2400,
        incarceration_min = 15,
        service_min = 15,
        allow_service = true,
    },
    murder = {
        label = "Murder",
        severity = 5,
        fine = 25000,
        incarceration_min = 120,
        service_min = 0,
        allow_service = false,
        banishment_days = 30,
    },
    jailbreak = {
        label = "Jailbreak",
        severity = 5,
        fine = 18000,
        incarceration_min = 90,
        service_min = 0,
        allow_service = false,
        banishment_days = 30,
    },
    contempt = {
        label = "Contempt",
        severity = 3,
        fine = 3500,
        incarceration_min = 15,
        service_min = 0,
        allow_service = false,
    },
    treason = {
        label = "Treason",
        severity = 5,
        fine = 50000,
        incarceration_min = 120,
        service_min = 0,
        allow_service = false,
        banishment_days = 60,
    },
    high_crimes_against_the_state = {
        label = "High Crimes Against the State",
        severity = 5,
        fine = 50000,
        incarceration_min = 120,
        service_min = 0,
        allow_service = false,
        banishment_days = 60,
    },
}

Justice.question_sets = {
    stocks = {
        { key = "city_name", prompt = "What is the name of the city you were charged in for your crimes?" },
        { key = "weekday_name", prompt = "What is today's day of the week?" },
        { key = "gender", prompt = "What is your gender?" },
    },
    jail = {
        { key = "hour_number", prompt = "What is the number of the current hour of the day in elven time?" },
        { key = "race", prompt = "What is your race?" },
        { key = "city_name", prompt = "What is the name of the city you were charged in for your crimes?" },
    },
}

Justice.service_verbs = {
    clean = { label = "CLEAN" },
    scrub = { label = "SCRUB" },
    dust = { label = "DUST" },
    polish = { label = "POLISH" },
    sort = { label = "SORT" },
    haul = { label = "HAUL" },
    rub = { label = "RUB" },
    push = { label = "PUSH" },
    slide = { label = "SLIDE" },
}

Justice.jurisdictions = {
    wehnimers_landing = {
        display_name = "Wehnimer's Landing",
        aliases = { "wehnimer's landing", "wehnimers landing", "landing", "wl" },
        zone_aliases = { "wehnimer's landing", "wehnimer's" },
        courtroom_room_id = 7972,
        clerk_room_id = 8686,
        jail_room_id = 33247,
        stockade_room_id = 3885,
        release_room_id = 3886,
        room_ids = { 8686, 7972, 3885, 3886, 3887, 3888, 3889, 15522, 15523, 15524, 19276, 33247 },
        service_tasks = {
            {
                key = "dock_sanding",
                label = "Sand the river dock",
                room_id = 3885,
                object_name = "dock",
                briefing = "Proceed to the prison courtyard dock and work the weathered boards until they are fit for use again.",
                inspect_intro = "The boards need a careful sequence. You must DUST loose grit away, RUB the wet stain free, then SLIDE the sandpaper with even pressure.",
                sequence = { "dust", "rub", "slide" },
                completion_text = "The dock boards look cleaner and smoother now.",
                cycles_required = 5,
            },
            {
                key = "court_records",
                label = "Order the court records",
                room_id = 3887,
                object_name = "records",
                briefing = "The constabulary has dumped half-sorted evidence ledgers in the prison office. Put them in proper order.",
                inspect_intro = "The ledgers are a mess. You must SORT the stack, DUST the shelf, then POLISH the bindings back into shape.",
                sequence = { "sort", "dust", "polish" },
                completion_text = "The records now sit in neat, usable order.",
                cycles_required = 4,
            },
        },
    },
    icemule_trace = {
        display_name = "Icemule Trace",
        aliases = { "icemule trace", "icemule", "imt", "mule" },
        zone_aliases = { "icemule trace", "icemule" },
        courtroom_room_id = 2458,
        clerk_room_id = 2458,
        jail_room_id = 33249,
        stockade_room_id = 2457,
        release_room_id = 2457,
        room_ids = { 2457, 2458, 33249 },
        service_tasks = {
            {
                key = "jail_scrub",
                label = "Scrub the jailhouse floor",
                room_id = 2458,
                object_name = "floor",
                briefing = "Scrub the tracked-in winter slush from the jailhouse floor.",
                inspect_intro = "The floor is a smear of grit and thawed ice. CLEAN the slush away, SCRUB the stubborn stains, then POLISH the boards dry.",
                sequence = { "clean", "scrub", "polish" },
                completion_text = "The jailhouse floor finally looks presentable.",
                cycles_required = 4,
            },
        },
    },
    solhaven = {
        display_name = "Solhaven",
        aliases = { "solhaven", "sol" },
        zone_aliases = { "solhaven" },
        courtroom_room_id = 12820,
        clerk_room_id = 13515,
        jail_room_id = 31434,
        stockade_room_id = 13515,
        release_room_id = 13515,
        room_ids = { 13515, 12820, 31434 },
        service_tasks = {
            {
                key = "guardhouse_lockers",
                label = "Restore the guardhouse lockers",
                room_id = 13515,
                object_name = "lockers",
                briefing = "The guardhouse lockers have fallen into rank disorder. Bring them back under control.",
                inspect_intro = "The lockers need methodical work. DUST the hinges, RUB old soot away, then SORT the stacked gear by size.",
                sequence = { "dust", "rub", "sort" },
                completion_text = "The guardhouse lockers are back in usable order.",
                cycles_required = 4,
            },
        },
    },
    ta_vaalor = {
        display_name = "Ta'Vaalor",
        aliases = { "ta'vaalor", "tavaalor", "vaalor", "tv" },
        zone_aliases = { "ta'vaalor", "ta'vaalor proper", "ta'vaalor, hall of justice" },
        courtroom_room_id = 10383,
        clerk_room_id = 3746,
        jail_room_id = 10419,
        stockade_room_id = 10419,
        pit_room_id = 33252,
        release_room_id = 10382,
        room_ids = { 3746, 10382, 10383, 10419, 33252 },
        service_tasks = {
            {
                key = "victory_dock",
                label = "Restore the Mistydeep dock",
                room_id = 10382,
                object_name = "dock",
                briefing = "Proceed to Victory Court and set the city dock back in order.",
                inspect_intro = "The dock is roughened by boots and river grit. DUST away the loose grit, RUB the stained planks, PUSH the warped brace back flush, then SLIDE the sandpaper across the grain.",
                sequence = { "dust", "rub", "push", "slide" },
                completion_text = "The dock timbers look fit for Vaalorian traffic again.",
                cycles_required = 5,
            },
            {
                key = "court_benches",
                label = "Restore the courtroom benches",
                room_id = 10383,
                object_name = "bench",
                briefing = "The Hall of Justice benches are scarred by restless prisoners. Restore them.",
                inspect_intro = "The bench row needs careful work. CLEAN the wax drips away, SCRUB the carved marks, then POLISH the finish back to a proper sheen.",
                sequence = { "clean", "scrub", "polish" },
                completion_text = "The benches look ready for another grim hearing.",
                cycles_required = 4,
            },
        },
    },
    ta_illistim = {
        display_name = "Ta'Illistim",
        aliases = { "ta'illistim", "taillistim", "illistim", "ti" },
        zone_aliases = { "ta'illistim", "ta'illistim, hall of justice" },
        courtroom_room_id = 1779,
        clerk_room_id = 1781,
        jail_room_id = 33251,
        stockade_room_id = 13179,
        pit_room_id = 33251,
        release_room_id = 1780,
        room_ids = { 1779, 1780, 1781, 13179, 33251, 33371 },
        service_tasks = {
            {
                key = "gaol_gallery",
                label = "Restore the gaol gallery",
                room_id = 33371,
                object_name = "gallery",
                briefing = "The gaol gallery is lined with grime and neglected brass. Bring it back to proper order.",
                inspect_intro = "The gallery wants a steady hand. DUST the railing, POLISH the brass, then SCRUB the staining from the flagstones.",
                sequence = { "dust", "polish", "scrub" },
                completion_text = "The gallery once again looks worthy of Illistim order.",
                cycles_required = 4,
            },
        },
    },
    zul_logoth = {
        display_name = "Zul Logoth",
        aliases = { "zul logoth", "zul", "zl" },
        zone_aliases = { "zul logoth", "zul" },
        courtroom_room_id = 9503,
        clerk_room_id = 9503,
        jail_room_id = 9447,
        stockade_room_id = 9446,
        pit_room_id = 33250,
        release_room_id = 9446,
        room_ids = { 9446, 9447, 9503, 16914, 16915, 16916, 33250 },
        service_tasks = {
            {
                key = "constabulary_gears",
                label = "Sort constabulary mining gear",
                room_id = 16915,
                object_name = "gear",
                briefing = "The constabulary has a mountain of confiscated mining gear that needs sorting.",
                inspect_intro = "The gear pile is mixed with dust and ore. SORT the picks and braces, DUST the rack, then HAUL the heavy crate back into place.",
                sequence = { "sort", "dust", "haul" },
                completion_text = "The confiscated gear now rests in a disciplined stack.",
                cycles_required = 4,
            },
        },
    },
    kharam_dzu = {
        display_name = "Kharam-Dzu",
        aliases = { "kharam-dzu", "kharam dzu", "teras", "kd" },
        zone_aliases = { "kharam-dzu", "ghorsa" },
        courtroom_room_id = 1959,
        clerk_room_id = 1959,
        jail_room_id = 33253,
        stockade_room_id = 14716,
        release_room_id = 14716,
        room_ids = { 1959, 14716, 14717, 33253 },
        service_tasks = {
            {
                key = "ghorsa_chain",
                label = "Repair the prison chains",
                room_id = 14717,
                object_name = "chains",
                briefing = "Ghorsa prison chains are rusting into uselessness. Set them right.",
                inspect_intro = "The chain rack is clogged with rust. RUB the links free, POLISH the iron, then SORT the repaired lengths onto the correct pegs.",
                sequence = { "rub", "polish", "sort" },
                completion_text = "The chain rack hangs in disciplined order again.",
                cycles_required = 4,
            },
        },
    },
    krakens_fall = {
        display_name = "Kraken's Fall",
        aliases = { "kraken's fall", "krakens fall", "kraken" },
        zone_aliases = { "kraken's fall", "krakens fall" },
        courtroom_room_id = 28970,
        clerk_room_id = 29127,
        jail_room_id = 33254,
        stockade_room_id = 29009,
        release_room_id = 29009,
        room_ids = { 29127, 28970, 29009, 33254 },
        service_tasks = {
            {
                key = "harbor_manifest",
                label = "Sort the harbor manifests",
                room_id = 29127,
                object_name = "manifests",
                briefing = "The constable wants the dock manifests sorted before another ship docks.",
                inspect_intro = "The manifests are damp and scattered. SORT the stacks, DUST the shelf, then POLISH the seal weights so they can be used again.",
                sequence = { "sort", "dust", "polish" },
                completion_text = "The harbor manifests are back under control.",
                cycles_required = 4,
            },
        },
    },
    mist_harbor = {
        display_name = "Mist Harbor",
        aliases = { "mist harbor", "mist harbour", "four winds", "fwi" },
        zone_aliases = { "mist harbor", "four winds isle", "four winds" },
        courtroom_room_id = 16695,
        clerk_room_id = 3659,
        jail_room_id = 33246,
        stockade_room_id = 3659,
        release_room_id = 3659,
        room_ids = { 3659, 16695, 33246 },
        service_tasks = {
            {
                key = "sergeants_desk",
                label = "Restore the sergeant's desk",
                room_id = 3659,
                object_name = "desk",
                briefing = "The sergeant's desk is buried in wax drips and sand. Put it back in order.",
                inspect_intro = "The desk is in rough shape. CLEAN the wax away, DUST the ledgers, then POLISH the wood smooth again.",
                sequence = { "clean", "dust", "polish" },
                completion_text = "The sergeant's desk is orderly once more.",
                cycles_required = 4,
            },
        },
    },
    rivers_rest = {
        display_name = "River's Rest",
        aliases = { "river's rest", "rivers rest", "rr" },
        zone_aliases = { "river's rest", "rivers rest" },
        courtroom_room_id = 10887,
        clerk_room_id = 10887,
        jail_room_id = 33248,
        stockade_room_id = 10887,
        release_room_id = 10887,
        room_ids = { 10887, 33248 },
        service_tasks = {
            {
                key = "brig_scrub",
                label = "Scrub the brig",
                room_id = 33248,
                object_name = "brig",
                briefing = "The brig stinks and the deck is foul. Make it usable again.",
                inspect_intro = "The brig needs hard labor. SCRUB the filth away, CLEAN the standing water, then HAUL the bucket back to the hatch.",
                sequence = { "scrub", "clean", "haul" },
                completion_text = "The brig is still grim, but no longer unfit for use.",
                cycles_required = 4,
            },
        },
    },
    cysaegir = {
        display_name = "Cysaegir",
        aliases = { "cysaegir", "cysa" },
        zone_aliases = { "cysaegir" },
        courtroom_room_id = 17142,
        clerk_room_id = 17141,
        jail_room_id = 33255,
        stockade_room_id = 17144,
        release_room_id = 17141,
        room_ids = { 17141, 17142, 17144, 17145, 17146, 17147, 33255 },
        service_tasks = {
            {
                key = "tribunal_gallery",
                label = "Restore the tribunal gallery",
                room_id = 17142,
                object_name = "gallery",
                briefing = "The tribunal gallery has to be made proper again before another hearing.",
                inspect_intro = "The gallery wants a methodical hand. DUST the carved rail, POLISH the brass fittings, then PUSH the bench braces back into alignment.",
                sequence = { "dust", "polish", "push" },
                completion_text = "The tribunal gallery looks orderly once more.",
                cycles_required = 4,
            },
        },
    },
}

Justice.npcs = {}

local function add_npc(template_id, name, title, description, room_id, jurisdiction_id, justice_role, service_tags)
    Justice.npcs[template_id] = {
        template_id = template_id,
        name = name,
        article = "",
        title = title,
        description = description,
        room_id = room_id,
        home_room_id = room_id,
        can_chat = true,
        can_emote = false,
        can_wander = false,
        can_combat = false,
        can_shop = false,
        dialogues = {
            default = "The official studies you with an expression honed by too many offenders."
        },
        hooks = { "on_player_talk" },
        lua_module = "globals.justice_npc",
        service_tags = service_tags or { "justice" },
        justice_role = justice_role,
        justice_jurisdiction = jurisdiction_id,
        lua_context = {
            justice_role = justice_role,
            justice_jurisdiction = jurisdiction_id,
        },
    }
end

add_npc("wl_justice_clerk", "Constable Deyl", "the justice clerk", "A weary constable with a habit of keeping every docket stacked in perfect order.", 8686, "wehnimers_landing", "clerk", { "justice", "clerk" })
add_npc("wl_justice_judge", "Magistrate Seln", "the magistrate", "A stern magistrate watches every movement with evident suspicion.", 7972, "wehnimers_landing", "judge", { "justice", "judge" })
add_npc("wl_justice_warden", "Jailer Harvek", "the warden", "The warden stands with keys looped across a broad leather belt.", 3887, "wehnimers_landing", "warden", { "justice", "warden" })
add_npc("wl_justice_watchman", "Watchman Brode", "the night watchman", "A hard-eyed watchman looks ready to hand out one more round of community labor.", 3885, "wehnimers_landing", "watchman", { "justice", "watchman" })

add_npc("imt_justice_clerk", "Deputy Nara", "the justice clerk", "A practical deputy keeps the Trace jailhouse papers tucked under one arm.", 2458, "icemule_trace", "clerk", { "justice", "clerk" })
add_npc("imt_justice_judge", "Deputy Nara", "the acting magistrate", "The same deputy has clearly handled both the paperwork and the sentencing for some time now.", 2458, "icemule_trace", "judge", { "justice", "judge" })
add_npc("imt_justice_warden", "Jailer Torf", "the jailer", "A hulking jailer stands beside the cell door with folded arms.", 2458, "icemule_trace", "warden", { "justice", "warden" })
add_npc("imt_justice_watchman", "Watchman Ovek", "the watchman", "A thick-furred watchman stamps slush from his boots and eyes you critically.", 2457, "icemule_trace", "watchman", { "justice", "watchman" })

add_npc("sol_justice_clerk", "Deputy Meren", "the justice clerk", "A Solhaven deputy flips through charge ledgers with clean, clipped efficiency.", 13515, "solhaven", "clerk", { "justice", "clerk" })
add_npc("sol_justice_judge", "Justice Talren", "the judge", "The judge's stare suggests you are not the first fool to stand here today.", 12820, "solhaven", "judge", { "justice", "judge" })
add_npc("sol_justice_warden", "Gaoler Venn", "the gaoler", "The gaoler stands with a keyring heavy enough to bruise.", 31434, "solhaven", "warden", { "justice", "warden" })
add_npc("sol_justice_watchman", "Watchman Ors", "the watchman", "A harbor watchman waits for trouble and expects to find it.", 13515, "solhaven", "watchman", { "justice", "watchman" })

add_npc("tv_justice_clerk", "Clerk Vael", "the justice clerk", "A Vaalorian clerk records every offense with unnerving calm.", 3746, "ta_vaalor", "clerk", { "justice", "clerk" })
add_npc("tv_justice_judge", "Magistrate Aralion", "the magistrate", "The magistrate carries the cold poise of Vaalorian authority.", 10383, "ta_vaalor", "judge", { "justice", "judge" })
add_npc("tv_justice_warden", "Stockade Captain Belis", "the stockade captain", "The stockade captain wears discipline as rigidly as armor.", 10419, "ta_vaalor", "warden", { "justice", "warden" })
add_npc("tv_justice_watchman", "Guardsman Elreth", "the night watchman", "A night watchman with river grit on his boots measures you like a burden to be assigned.", 10382, "ta_vaalor", "watchman", { "justice", "watchman" })

add_npc("ti_justice_clerk", "Clerk Silaris", "the justice clerk", "An austere elven clerk tends immaculate charge rolls.", 1781, "ta_illistim", "clerk", { "justice", "clerk" })
add_npc("ti_justice_judge", "Tribunal Voice Elaran", "the magistrate", "The tribunal's voice is cool, precise, and utterly unimpressed.", 1779, "ta_illistim", "judge", { "justice", "judge" })
add_npc("ti_justice_warden", "Gaoler Mereth", "the gaoler", "A gaoler in immaculate attire watches the corridor without blinking.", 33371, "ta_illistim", "warden", { "justice", "warden" })
add_npc("ti_justice_watchman", "Official Nirel", "the city official", "The official's patient smile promises extra labor for any fool who wastes time.", 13179, "ta_illistim", "watchman", { "justice", "watchman" })

add_npc("zl_justice_clerk", "Constable Brohn", "the constable", "A broad-shouldered constable smells faintly of lamp oil and mine dust.", 9503, "zul_logoth", "clerk", { "justice", "clerk" })
add_npc("zl_justice_judge", "Marshal Kharz", "the magistrate", "The marshal's blunt gaze says all arguments will be brief.", 9503, "zul_logoth", "judge", { "justice", "judge" })
add_npc("zl_justice_warden", "Jailer Droth", "the jailer", "The jailer keeps a steel ring of keys in one hand and a cudgel in the other.", 9447, "zul_logoth", "warden", { "justice", "warden" })
add_npc("zl_justice_watchman", "Watchman Thorr", "the watchman", "A stocky watchman watches you like he is already planning the next task.", 9446, "zul_logoth", "watchman", { "justice", "watchman" })

add_npc("kd_justice_clerk", "Deputy Commander Rul", "the justice clerk", "The deputy commander keeps both grievances and sentencing in a single battered ledger.", 1959, "kharam_dzu", "clerk", { "justice", "clerk" })
add_npc("kd_justice_judge", "Commander Kiramon", "the commander", "The commander's scarred face leaves little room for hope.", 1959, "kharam_dzu", "judge", { "justice", "judge" })
add_npc("kd_justice_warden", "Warden Ghorsa", "the warden", "The warden moves with the confidence of a man used to breaking escapes before they begin.", 14717, "kharam_dzu", "warden", { "justice", "warden" })
add_npc("kd_justice_watchman", "Deputy Dorn", "the deputy", "A dwarven deputy looks delighted at the thought of assigning filthy work.", 14716, "kharam_dzu", "watchman", { "justice", "watchman" })

add_npc("kf_justice_clerk", "Constable Aris", "the constable", "A sea-weathered constable sorts docket slips beneath a cracked lantern.", 29127, "krakens_fall", "clerk", { "justice", "clerk" })
add_npc("kf_justice_judge", "Magistrate Rusk", "the magistrate", "The magistrate's coat is immaculate despite the harbor damp.", 28970, "krakens_fall", "judge", { "justice", "judge" })
add_npc("kf_justice_warden", "Gaoler Pike", "the gaoler", "The gaoler smells of brine, tar, and contempt.", 29009, "krakens_fall", "warden", { "justice", "warden" })
add_npc("kf_justice_watchman", "Watchman Farl", "the watchman", "A harbor watchman watches the tide and you with equal distrust.", 29127, "krakens_fall", "watchman", { "justice", "watchman" })

add_npc("mh_justice_clerk", "Sergeant Hallen", "the justice clerk", "A Four Winds sergeant balances courtesy and impatience with long practice.", 3659, "mist_harbor", "clerk", { "justice", "clerk" })
add_npc("mh_justice_judge", "Magistrate Orlin", "the magistrate", "The magistrate holds court with island-bred certainty.", 16695, "mist_harbor", "judge", { "justice", "judge" })
add_npc("mh_justice_warden", "Jailer Tess", "the jailer", "The jailer watches every hand and pocket with sharp attention.", 33246, "mist_harbor", "warden", { "justice", "warden" })
add_npc("mh_justice_watchman", "Watchman Lerris", "the watchman", "A watchman studies you like unfinished paperwork.", 3659, "mist_harbor", "watchman", { "justice", "watchman" })

add_npc("rr_justice_clerk", "Captain Olvar", "the captain", "The captain's room doubles as court, office, and place of bad news.", 10887, "rivers_rest", "clerk", { "justice", "clerk" })
add_npc("rr_justice_judge", "Captain Olvar", "the acting magistrate", "The captain clearly sees no reason to separate law from command.", 10887, "rivers_rest", "judge", { "justice", "judge" })
add_npc("rr_justice_warden", "Brigmaster Wen", "the brigmaster", "The brigmaster rattles the lock as if to remind you who holds the key.", 33248, "rivers_rest", "warden", { "justice", "warden" })
add_npc("rr_justice_watchman", "Watchman Pell", "the watchman", "A river watchman squints at you across the damp planks.", 10887, "rivers_rest", "watchman", { "justice", "watchman" })

add_npc("cysa_justice_clerk", "Reformatory Clerk Sael", "the clerk", "A crisp clerk keeps every Cysaegir detention record immaculately ordered.", 17141, "cysaegir", "clerk", { "justice", "clerk" })
add_npc("cysa_justice_judge", "Tribunal Magistrate Elyra", "the magistrate", "The magistrate's attention is cool and total.", 17142, "cysaegir", "judge", { "justice", "judge" })
add_npc("cysa_justice_warden", "Warden Teral", "the warden", "The warden's measured pace never strays far from the cells.", 17145, "cysaegir", "warden", { "justice", "warden" })
add_npc("cysa_justice_watchman", "Official Caerel", "the official", "A tribunal official holds a slate of labor assignments close to the chest.", 17144, "cysaegir", "watchman", { "justice", "watchman" })

return Justice
