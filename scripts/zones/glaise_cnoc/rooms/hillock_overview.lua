-- Room 5867: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5867
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Here atop the hillock, you see the original section of the cemetery spreading out before you to the north.  Even from this distance it is obvious that the plots around the perimeter of the cemetery are much newer.  To the south you can see the gates marking the entrance to the cemetery.  The iron fence that encloses the cemetery is easy to identify, even where the local flora tries to obscure it."

Room.exits = {
    north                    = 5868,
    southeast                = 5836,
    southwest                = 5866,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
