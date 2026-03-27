-- Room 5836: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5836
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A small plot of five headstones is enclosed by a low border of cut granite blocks.  Wild violets grow between the markers, providing a splash of purple to the green grass blanketing the resting place."

Room.exits = {
    southwest                = 5835,
    northeast                = 5837,
    northwest                = 5867,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
