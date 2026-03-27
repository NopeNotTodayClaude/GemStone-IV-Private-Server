-- Room 10556: Lunule Weald, Slade
local Room = {}

Room.id          = 10556
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "Several small piles of rocks appear to be scattered haphazardly through the thick grass.  Many of the rocks are painted black or silver, and the piles are set into different shapes.  Though the grass is thick, it doesn't encroach upon the strange piles of rocks."

Room.exits = {
    northeast                = 10541,
    northwest                = 10548,
    west                     = 10549,
    east                     = 10557,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
