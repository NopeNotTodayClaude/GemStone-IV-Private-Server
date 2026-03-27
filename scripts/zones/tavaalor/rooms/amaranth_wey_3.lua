-- Room 3489: Ta'Vaalor, Amaranth Wey
local Room = {}

Room.id          = 3489
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Wey"
Room.description = "A small fountain presides over the intersection of cobbled streets, its centerpiece a carved marble statue of Phoen.  The thick, low walls of the fountain provide a lovely resting spot from which to watch the passersby as they move along the wey."

Room.exits = {
    west                 = 3492,
    east                 = 3490,
    northwest            = 3488,
    go_meetinghall       = 10330,
    go_barracks          = 27924,
}

Room.indoor = false
Room.safe   = true

return Room
