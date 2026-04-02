local Ferries = {}

Ferries.lake_of_fear = {
    id = "lake_of_fear",
    name = "Lake of Fear Ferry",
    ferry_room_id = 10118,
    onboard_room_ids = { 10118, 13977 },
    boarding_exit = "go_plank",
    dock_duration_sec = 60,
    travel_duration_sec = 120,
    start_side = "south",
    ferry_look = "The broad wooden ferry rides low in the dark water, its striped awning stirring gently as the crew readies the crossing.",
    ferryman_look = "The ferryman watches the dock with the calm patience of someone who has made this crossing more times than anyone could count.",
    onboard_depart_msg = "The ferry eases away from the dock and begins gliding across the eerily still waters of the lake.",
    onboard_arrive_msg = "The ferry bumps softly against the dock and a plank is lowered for passengers.",
    sides = {
        north = {
            room_id = 10117,
            fare = 100,
            entity_line = "You also see a broad wooden ferry moored at the dock.",
            ferryman_line = "You also see a ferryman waiting beside the lowered plank.",
            board_msg = "The ferryman collects 100 silvers from you and waves you toward the plank.",
            deny_msg = "\"The fare is 100 silvers,\" the ferryman says, planting himself in your way.",
            departure_room_msg = "A broad wooden ferry pushes away from the dock and heads out across the lake.",
            arrival_room_msg = "A broad wooden ferry glides in from across the lake and bumps gently against the dock.",
        },
        south = {
            room_id = 10119,
            fare = 0,
            entity_line = "You also see a broad wooden ferry moored at the dock.",
            ferryman_line = "You also see a ferryman steadying the lowered plank.",
            board_msg = "The ferryman gives you a curt nod and gestures you toward the plank.",
            deny_msg = "",
            departure_room_msg = "A broad wooden ferry pushes away from the dock and glides northward across the lake.",
            arrival_room_msg = "A broad wooden ferry emerges from the dark water and noses up to the dock.",
        },
    },
}

Ferries.locksmehr_river = {
    id = "locksmehr_river",
    name = "Locksmehr River Ferry",
    ferry_room_id = 1191,
    onboard_room_ids = { 1191 },
    boarding_exit = "go_plank",
    dock_duration_sec = 60,
    travel_duration_sec = 60,
    start_side = "north",
    ferry_look = "The shallow-draft ferryboat rides the thick guide rope stretched across the Locksmehr, its narrow walkway wet with spray from the rushing current.",
    ferryman_look = "The blind ferryman works by feel and habit, one hand never far from the guide rope that keeps the ferry on its line.",
    onboard_depart_msg = "The blind ferryman leans into his pole and the ferry shudders away from the dock, following the guide rope across the current.",
    onboard_arrive_msg = "The ferry bumps against the dock and the blind ferryman lowers the plank for disembarking passengers.",
    sides = {
        north = {
            room_id = 1190,
            fare = 10,
            entity_line = "You also see a shallow-draft ferryboat tied off beside the dock.",
            ferryman_line = "You also see a blind ferryman holding out a weathered hand for the toll.",
            board_msg = "The blind ferryman takes your 10 silvers and tilts his head toward the plank.",
            deny_msg = "\"Ten silvers for the crossing,\" the blind ferryman says, refusing to budge.",
            departure_room_msg = "The ferry shudders loose from the dock and begins sliding along the guide rope toward the opposite bank.",
            arrival_room_msg = "A shallow-draft ferryboat glides in along the guide rope and nudges against the dock.",
        },
        south = {
            room_id = 1192,
            fare = 10,
            entity_line = "You also see a shallow-draft ferryboat tied off beside the dock.",
            ferryman_line = "You also see a blind ferryman waiting by the lowered plank.",
            board_msg = "The blind ferryman accepts 10 silvers from you and motions you aboard.",
            deny_msg = "\"Ten silvers for the crossing,\" the blind ferryman says, barring the plank.",
            departure_room_msg = "The ferryboat eases away from the dock and begins creeping across the river on its guide rope.",
            arrival_room_msg = "A shallow-draft ferryboat creeps in along the guide rope and knocks against the dock.",
        },
    },
}

return Ferries
