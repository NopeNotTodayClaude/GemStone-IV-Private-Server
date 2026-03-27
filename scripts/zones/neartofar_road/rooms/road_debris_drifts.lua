-- Room 31443: Neartofar Road
local Room = {}

Room.id          = 31443
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Drifts of debris line the road as it follows a straight path through columns of oaks and larches.  Gravel mixes with the rubble, creating an uneven path.  Bits of broken cobbles peek out from the piles covering the surface."

Room.exits = {
    northwest                = 10498,
    southeast                = 31444,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
