-- Room 5890: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5890
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Looking far to the north from atop the hill, a dark plain can be seen.  A pair of bleached white walls ring the area, concealing much of the terrain.  A network of chains hangs between the two walls, its purpose not apparent at this distance.  The black ruins of a tower rise up ominously from the central area."

Room.exits = {
    north                    = 5891,
    south                    = 5882,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
