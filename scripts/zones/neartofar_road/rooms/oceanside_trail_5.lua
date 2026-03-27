-- Room 31478: Oceanside Forest, Trail
local Room = {}

Room.id          = 31478
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Trail"
Room.description = "Spreading out across the sky, thick branches filled with leaves sway above.  Small saplings stretch up from the rich foliage in imitation of their larger brethren.  The songs of wild birds fill the highest limbs as the colorful avians fly about."

Room.exits = {
    west                     = 31477,
    southeast                = 31479,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
