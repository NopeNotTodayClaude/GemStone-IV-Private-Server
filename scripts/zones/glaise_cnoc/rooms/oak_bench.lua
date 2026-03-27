-- Room 5842: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5842
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The path curves towards the north here, still following the iron fence.  Under the shade of a large oak tree, a wooden bench provides visitors a place to sit and relax, or quietly contemplate what has brought them here."

Room.exits = {
    southwest                = 5841,
    north                    = 5843,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
