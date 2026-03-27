-- Room 31482: Oceanside Forest, Trail
local Room = {}

Room.id          = 31482
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Trail"
Room.description = "Winding through the woodland, the road's surface is cushioned with crushed shells and sand.  Sharp and tangy, the scent of sea and salt fills the air, while the sounds of crashing waves carry throughout the area.  Shrubs and bushes are more prominent than the taller trees that grow more abundant towards the interior of the forest."

Room.exits = {
    northwest                = 31481,
    east                     = 31483,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
