-- Room 5878: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5878
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Headstones flank both sides of the gravel path here.  Weatherworn, the headstones in this area are obviously older than those which follow the fence enclosing the cemetery.  The gravel path crunches underfoot, but provides an easy route to follow."

Room.exits = {
    east                     = 5879,
    west                     = 5877,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
