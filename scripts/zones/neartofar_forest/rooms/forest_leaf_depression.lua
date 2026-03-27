-- Room 10627: Neartofar Forest
local Room = {}

Room.id          = 10627
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "The trail passes through a deep depression ringed by a double row of oak trees.  For years, it seems, the autumn winds have blown their leaves into the depression until the detritus lies nearly a foot deep in places.  The glade reeks with the acrid smells of mold and decay."

Room.exits = {
    northwest                = 10626,
    southeast                = 10628,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
