-- Room 5844: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5844
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The landscape here is dotted with small white grave markers.  Scattered among the markers, purple, white and pink wildflowers grow undisturbed.  A cool breeze rustles the leaves of a stately oak tree.  To the northwest the path inclines slightly as it climbs a small hillock."

Room.exits = {
    south                    = 5843,
    northwest                = 5845,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
