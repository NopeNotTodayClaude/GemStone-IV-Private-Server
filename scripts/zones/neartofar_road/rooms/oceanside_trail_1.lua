-- Room 31474: Oceanside Forest, Trail
local Room = {}

Room.id          = 31474
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Trail"
Room.description = "Sea rosemary shrubs close in on the narrow road, creating a beautiful border for the rugged terrain.  Pale, sandy pebbles cover the partially cleared trail.  The sounds of small creatures moving about the forest fill the air, occasionally drowned out by the variety of birds singing in the trees."

Room.exits = {
    northwest                = 31473,
    east                     = 31475,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
