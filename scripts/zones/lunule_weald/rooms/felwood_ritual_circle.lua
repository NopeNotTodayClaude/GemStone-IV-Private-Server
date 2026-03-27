-- Room 10570: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10570
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "In the midst of the dark trees is a circular area surrounded by black and silver painted rocks.  Inside the circle, all undergrowth, leaves and branches have been cleared and burned to leave only the bare soil.  A pool of reddish-brown liquid had been spilled onto the soil in the center of the circle at some point in the past, leaving it slightly darker than the surrounding dirt."

Room.exits = {
    northeast                = 10569,
    west                     = 10571,
    north                    = 10574,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
