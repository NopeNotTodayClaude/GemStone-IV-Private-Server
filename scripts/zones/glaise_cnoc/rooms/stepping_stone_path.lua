-- Room 5886: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5886
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Crushed granite forms the pathway through an open area of grass free of graves.  A white marble stepping stone, in the shape of a star, is set into the crushed granite that forms the walkway.  Ancient markings adorn the stone, their meaning a mystery."

Room.exits = {
    north                    = 5885,
    south                    = 5887,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
