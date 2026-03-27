-- Room 31446: Neartofar Road
local Room = {}

Room.id          = 31446
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Burry chestnuts fill the gaps where cobbles have come loose in the old road.  In a particularly large rut, a puddle has formed, its moisture an attractant to various insects, from mayflies to gnats.  Massive chestnut trees with smooth grey trunks stand sentinel along the edge of the road."

Room.exits = {
    northwest                = 31445,
    south                    = 31447,
    northeast                = 34448,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
