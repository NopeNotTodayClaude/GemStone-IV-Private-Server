-- Room 5849: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5849
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "To the east, a verdigris statue sits atop a granite pedestal several feet from the path.  Covered with fragrant honeysuckle, the iron fence forms a beautiful backdrop for the statue."

Room.exits = {
    southeast                = 5848,
    northwest                = 5850,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
