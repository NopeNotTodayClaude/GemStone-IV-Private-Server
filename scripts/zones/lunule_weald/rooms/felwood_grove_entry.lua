-- Room 10547: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10547
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "Dead leaves and undergrowth surround a large boulder at the edge of a dark forest of fel trees.  The screech of an owl deep in the gloom of the forest echoes eerily in the silence."

Room.exits = {
    northwest                = 10546,
    go_boulder               = 10555,
    east                     = 10559,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
