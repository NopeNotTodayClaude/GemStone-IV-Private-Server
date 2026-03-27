-- Room 31453: Neartofar Road
local Room = {}

Room.id          = 31453
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Cobbles stand like miniature formations in what has become nothing more than a muddy, wide, corrugated pathway.  Fallen trees in various stages of decay are scattered about the side of the road.  Piles of moss-covered debris drift against the natural barriers."

Room.exits = {
    northwest                = 31452,
    south                    = 31454,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
