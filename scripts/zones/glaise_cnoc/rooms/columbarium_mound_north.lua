-- Room 5880: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5880
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The gravel path continues to the northwest.  However, to the south, a grassy mound interrupts the path.  Atop the mound a large monument is visible.  The iron fence enclosing the cemetery is close to the path here, barely an arms-length away."

Room.exits = {
    south                    = 5876,
    northwest                = 5871,
    go_structure             = 10677,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
