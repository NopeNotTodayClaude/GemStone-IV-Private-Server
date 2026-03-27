-- Room 31451: Neartofar Road
local Room = {}

Room.id          = 31451
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Piles of leaves and other natural debris drift over the earthen road.  Bits of ancient cobblestone peek from underneath layers of dirt and greenery.  Arching overhead, a row of white oak trees shelter the road with their verdant canopy.  Thin rays of sunlight stream through small gaps in the thick, intertwined branches."

Room.exits = {
    northwest                = 31450,
    southeast                = 31452,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
