-- Room 10648: Neartofar Forest
local Room = {}

Room.id          = 10648
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "The trail passes through some red maples that, over the course of seasons, have littered the forest floor with myriad leaves.  The trail is wider than can be accounted for by the passage of an occasional traveler.  Some tusk-marks at the base of the maples suggest that perhaps the local fauna created the trail as a run to the nearby water."

Room.exits = {
    southeast                = 10642,
    northwest                = 10649,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
