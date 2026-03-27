-- Room 10551: Lunule Weald, Slade
local Room = {}

Room.id          = 10551
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "A wide, zigzagged trail of flattened grass meanders off into the distance.  Several small saplings lay trampled to death, their tiny leaves brown and rotting."

Room.exits = {
    west                     = 10550,
    southeast                = 10552,
    east                     = 10558,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
