-- Room 5891: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5891
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A carpet of green grass fills the area, only interrupted by a scattering of fallen leaves.  A nearby monir seems to be the source of the leaves.  The tree's branches are regularly trimmed to keep them from hanging too low.  To the south, the path begins a gentle ascent up a hillside."

Room.exits = {
    northeast                = 5852,
    northwest                = 5850,
    south                    = 5890,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
