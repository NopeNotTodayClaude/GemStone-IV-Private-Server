-- Room 10636: Neartofar Forest
local Room = {}

Room.id          = 10636
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "In a small hollow between the trees, rainwater collects into a small pond.  Covered with lily pads in various shades of green, the water remains perfectly still...until a loud *SPLASH* signals the presence of a large frog or fish.  A few elm trees mingle with the oaks, their branches reaching up to the sky in a gesture of loving adoration."

Room.exits = {
    south                    = 10635,
    north                    = 10637,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
