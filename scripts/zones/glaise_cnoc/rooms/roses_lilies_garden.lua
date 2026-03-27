-- Room 5857: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5857
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A riot of color and scents assaults the senses here.  Roses and lilies, in a myriad of colors, grow in a large cultivated garden along the fence.  Black and yellow striped bumblebees flit from flower to flower, their legs yellow with pollen."

Room.exits = {
    southwest                = 5856,
    northeast                = 5858,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
