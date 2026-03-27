-- Room 5855: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5855
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "To the southwest a field of green opens up, bordered by the iron fence enclosing the cemetery.  Unchecked vines cover much of the fence, creating a wall of green.  The stump of a monir tree is all that remains to mark where the tree once stood."

Room.exits = {
    southwest                = 5854,
    northeast                = 5856,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
