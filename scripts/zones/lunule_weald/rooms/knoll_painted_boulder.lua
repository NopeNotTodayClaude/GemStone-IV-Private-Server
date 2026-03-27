-- Room 10555: Lunule Weald, Knoll
local Room = {}

Room.id          = 10555
Room.zone_id     = 8
Room.title       = "Lunule Weald, Knoll"
Room.description = "Dead leaves and grass surround a large boulder set in the middle of the path.  The face of the boulder has been painted with odd symbols, figures and letters.  Several of the symbols resemble crescent moons, though they appear misshapen."

Room.exits = {
    northeast                = 10546,
    go_boulder               = 10547,
    northwest                = 10554,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
