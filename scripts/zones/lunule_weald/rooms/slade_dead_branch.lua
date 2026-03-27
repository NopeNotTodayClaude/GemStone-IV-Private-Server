-- Room 10542: Lunule Weald, Slade
local Room = {}

Room.id          = 10542
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "A large, dead branch is stuck into the ground and circled by black and silver painted rocks.  No grass grows near the branch, though the dirt surrounding it appears fertile.  There is no breeze, and the air is deathly silent."

Room.exits = {
    northwest                = 10541,
    southeast                = 10543,
    west                     = 10557,
    southwest                = 10558,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
