-- Room 10543: Lunule Weald, Slade
local Room = {}

Room.id          = 10543
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "Several figures formed of dead sticks and branches have been forced into the ground at irregular intervals.  The figures themselves are tied together with rotting leather and many are wearing tattered rags.  Not all of the figures are complete, some are missing heads or limbs."

Room.exits = {
    northwest                = 10542,
    west                     = 10544,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
