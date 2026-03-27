-- Room 59031: Scenario 3 - Rendezvous point
local Room = {}

Room.id          = 59031
Room.zone_id     = 99
Room.title       = "Dead End Alley"
Room.description = "The alley ends at a blank stone wall.  Stacked crates form a makeshift meeting area.  A cloaked figure lurks here, nervously shifting from foot to foot, clutching a small parcel under one arm."

Room.exits = {
    west = 59030,
}

Room.indoor = false
Room.safe   = true

return Room
