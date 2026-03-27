-- Room 5875: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5875
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The gravel path continues to the southwest.  However, to the north, a grassy mound interrupts the path.  Atop the mound a large monument is visible.  The iron fence enclosing the cemetery is close to the path here, barely an arms-length away."

Room.exits = {
    north                    = 5876,
    southwest                = 5874,
    go_structure             = 10684,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
