-- Room 100: Town Square Central
-- The heart of Wehnimer's Landing

local Room = {}

Room.id          = 100
Room.zone_id     = 1
Room.title       = "Town Square Central"
Room.description = "This is the center of the main square of Wehnimer's Landing.  The square is paved with cobblestones and surrounded by shops and homes.  Townspeople bustle about, going about their daily business.  A large well-kept fountain dominates the center of the square, its water sparkling in the light."

Room.exits = {
    north = 101,
    south = 102,
    east  = 103,
    west  = 104,
    northeast = 105,
    northwest = 106,
    southeast = 107,
    southwest = 108,
}

Room.indoor    = false
Room.safe      = true
Room.supernode = true

return Room
