-- Room 5854: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5854
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The gnarled roots of a haon tree snake across the path here.  Sunlight filters through the canopy of leaves that rustle in the breeze.  Moss clinging to the trunk of the haon tree stands out green against the light grey bark."

Room.exits = {
    southwest                = 5853,
    northeast                = 5855,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
