-- Room 10629: Neartofar Forest, Riverside
local Room = {}

Room.id          = 10629
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Riverside"
Room.description = "At the side of the river, silt-black soil supports the growth of black willow trees that whistle in a gentle breeze.  Trailing their long, thin branches into the water, the willows are also fed by the tiny streams that carry runoff from the tall ridge to the east.  As a result, the bottom land remains perpetually soggy, making travel through the area a messy and tiring proposition."

Room.exits = {
    southeast                = 10625,
    north                    = 10630,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
