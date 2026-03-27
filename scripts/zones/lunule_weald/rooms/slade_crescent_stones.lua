-- Room 10558: Lunule Weald, Slade
local Room = {}

Room.id          = 10558
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "In the center of a circular area completely devoid of grass is a crescent-moon shape formed with small round, flat stones.  Each stone is painted a different color, and several of the stones have odd symbols on them.  The soil inside the circle has not been disturbed by footprints or other markings."

Room.exits = {
    northeast                = 10542,
    east                     = 10544,
    west                     = 10551,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
