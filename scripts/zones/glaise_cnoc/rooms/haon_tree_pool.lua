-- Room 5888: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5888
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A small spring-fed pool sits in the shade of a haon tree.  Small insects appear to skate across the surface of the water.  Despite the tiny ripples created by the insects, the surface of the water reflects a mirror image of the haon tree.  A granite bench, near the pool, provides a serene place to sit and relax."

Room.exits = {
    east                     = 5879,
    west                     = 5889,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
